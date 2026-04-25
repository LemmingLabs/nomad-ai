import logging
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
from app.services.storage_service import StorageService


logger = logging.getLogger(__name__)


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
        self.storage_service = StorageService()

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

        destination_path, stored_filename = self._build_storage_path(
            business_id=place.business_id,
            place_id=place.id,
            original_filename=file.filename,
            content_type=content_type,
        )

        stored_url: str | None = None
        try:
            stored_url = self.storage_service.upload_bytes(
                file_bytes,
                destination_path=destination_path,
                content_type=content_type,
            )
            return self.media_repo.create(
                sponsored_place_id=place.id,
                type=type,
                url=stored_url,
                filename=stored_filename,
                content_type=content_type,
            )
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exc),
            ) from exc
        except Exception:
            if stored_url:
                try:
                    self.storage_service.delete_by_url(stored_url)
                except Exception:
                    logger.exception("[SPONSORED MEDIA] Failed to rollback uploaded media url=%s", stored_url)
            raise
        finally:
            await file.close()

    def delete_my_place_media(self, current_user: User, *, place_id: int, media_id: int) -> None:
        place = self.place_service.get_my_place(current_user, place_id)
        media = self.media_repo.get_for_place(place.id, media_id)
        if media is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsored place media not found")

        try:
            self.storage_service.delete_by_url(media.url)
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exc),
            ) from exc
        self.media_repo.delete(media)

    def _build_storage_path(
        self,
        *,
        business_id: int,
        place_id: int,
        original_filename: str | None,
        content_type: str,
    ) -> tuple[str, str]:
        safe_name = self._sanitize_filename(original_filename)
        extension = Path(safe_name).suffix.lower()
        expected_extension = self.ALLOWED_CONTENT_TYPES[content_type]
        if extension not in self.ALLOWED_CONTENT_TYPES.values():
            extension = expected_extension
        stem = Path(safe_name).stem or "image"
        stored_filename = f"{stem}-{uuid4().hex}{extension}"
        storage_path = Path("media") / "businesses" / str(business_id) / "sponsored_places" / str(place_id) / stored_filename
        return storage_path.as_posix(), stored_filename

    def _sanitize_filename(self, filename: str | None) -> str:
        raw_name = Path(filename or "image").name
        normalized = unicodedata.normalize("NFKD", raw_name).encode("ascii", "ignore").decode("ascii")
        cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", normalized).strip("._-")
        return cleaned or "image"
