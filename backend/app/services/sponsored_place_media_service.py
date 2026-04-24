import re
import unicodedata
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.sponsored_place_media import SponsoredPlaceMedia, SponsoredPlaceMediaType
from app.models.user import User
from app.repositories.sponsored_place_media_repository import SponsoredPlaceMediaRepository
from app.services.sponsored_place_service import SponsoredPlaceService


class SponsoredPlaceMediaService:
    ALLOWED_CONTENT_TYPES = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

    def __init__(self, db: Session):
        self.db = db
        self.place_service = SponsoredPlaceService(db)
        self.media_repo = SponsoredPlaceMediaRepository(db)
        self.media_root = Path(__file__).resolve().parents[2] / "media"

    def list_my_place_media(self, current_user: User, place_id: int) -> list[SponsoredPlaceMedia]:
        place = self.place_service.get_my_place(current_user, place_id)
        return self.media_repo.list_for_place(place.id)

    async def upload_my_place_media(
        self,
        current_user: User,
        *,
        place_id: int,
        type: SponsoredPlaceMediaType,
        file: UploadFile,
    ) -> SponsoredPlaceMedia:
        place = self.place_service.get_my_place(current_user, place_id)
        content_type = (file.content_type or "").lower().strip()
        if content_type not in self.ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Allowed types: image/jpeg, image/png, image/webp",
            )

        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty",
            )
        if len(file_bytes) > self.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File is too large. Maximum size is {self.MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB",
            )

        relative_url, absolute_path, stored_filename = self._build_storage_path(
            business_id=place.business_id,
            place_id=place.id,
            original_filename=file.filename,
            content_type=content_type,
        )
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_bytes(file_bytes)

        try:
            return self.media_repo.create(
                sponsored_place_id=place.id,
                type=type,
                url=relative_url,
                filename=stored_filename,
                content_type=content_type,
            )
        except Exception:
            if absolute_path.exists():
                absolute_path.unlink()
            raise
        finally:
            await file.close()

    def delete_my_place_media(self, current_user: User, *, place_id: int, media_id: int) -> None:
        place = self.place_service.get_my_place(current_user, place_id)
        media = self.media_repo.get_for_place(place.id, media_id)
        if media is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsored place media not found")

        file_path = self._file_path_from_url(media.url)
        self.media_repo.delete(media)
        if file_path.exists():
            file_path.unlink()

    def _build_storage_path(
        self,
        *,
        business_id: int,
        place_id: int,
        original_filename: str | None,
        content_type: str,
    ) -> tuple[str, Path, str]:
        safe_name = self._sanitize_filename(original_filename)
        extension = Path(safe_name).suffix.lower()
        expected_extension = self.ALLOWED_CONTENT_TYPES[content_type]
        if extension not in self.ALLOWED_CONTENT_TYPES.values():
            extension = expected_extension
        stem = Path(safe_name).stem or "image"
        stored_filename = f"{stem}-{uuid4().hex}{extension}"
        relative_path = Path("businesses") / str(business_id) / "sponsored_places" / str(place_id) / stored_filename
        relative_url = f"/media/{relative_path.as_posix()}"
        return relative_url, self.media_root / relative_path, stored_filename

    def _file_path_from_url(self, url: str) -> Path:
        relative = url.removeprefix("/media/").lstrip("/")
        return self.media_root / relative

    def _sanitize_filename(self, filename: str | None) -> str:
        raw_name = Path(filename or "image").name
        normalized = unicodedata.normalize("NFKD", raw_name).encode("ascii", "ignore").decode("ascii")
        cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", normalized).strip("._-")
        return cleaned or "image"
