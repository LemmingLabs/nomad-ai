import logging
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse

from app.core.config import settings


logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self) -> None:
        self.media_root = Path(__file__).resolve().parents[2] / "media"
        self._client = None

    def upload_bytes(
        self,
        content: bytes,
        *,
        destination_path: str,
        content_type: str,
    ) -> str:
        normalized_path = self._normalize_destination_path(destination_path)
        content_type = content_type or "application/octet-stream"

        if self._uses_gcs():
            blob = self._get_bucket().blob(normalized_path)
            blob.upload_from_string(content, content_type=content_type)
            blob.cache_control = "private, max-age=31536000"
            blob.patch()
            return normalized_path

        local_relative_path = self._local_relative_path(normalized_path)
        absolute_path = self.media_root / local_relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_bytes(content)
        return f"/media/{local_relative_path.as_posix()}"

    def get_access_url(self, stored_path_or_url: str) -> str:
        value = str(stored_path_or_url or "").strip()
        if not value:
            return value
        if value.startswith("http://") or value.startswith("https://"):
            return value

        if not self._uses_gcs():
            return value

        try:
            return self._generate_signed_url(value)
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(f"Failed to generate signed URL for object '{value}': {exc}") from exc

    def delete(self, stored_path_or_url: str) -> None:
        if self._uses_gcs():
            parsed = urlparse(str(stored_path_or_url or "").strip())
            if parsed.netloc:
                object_path = parsed.path.lstrip("/")
                bucket_name = (settings.GCS_BUCKET_NAME or "").strip()
                if bucket_name and object_path.startswith(f"{bucket_name}/"):
                    object_path = object_path[len(bucket_name) + 1 :]
            else:
                object_path = self._normalize_destination_path(stored_path_or_url)
            if not object_path:
                logger.warning("[STORAGE] Could not resolve GCS object path from stored value: %s", stored_path_or_url)
                return

            try:
                self._get_bucket().blob(object_path).delete()
            except Exception as exc:
                if self._is_gcs_not_found(exc):
                    logger.warning("[STORAGE] GCS object already missing: %s", stored_path_or_url)
                    return
                raise
            logger.info("[STORAGE] deleted: %s", stored_path_or_url)
            return

        absolute_path = self._local_path_from_url(stored_path_or_url)
        if absolute_path is None:
            logger.warning("[STORAGE] Could not resolve local media path from URL: %s", stored_path_or_url)
            return
        if absolute_path.exists():
            absolute_path.unlink()
            logger.info("[STORAGE] deleted: %s", stored_path_or_url)

    def delete_by_url(self, url: str) -> None:
        self.delete(url)

    def _uses_gcs(self) -> bool:
        return settings.STORAGE_BACKEND == "gcs"

    def _get_bucket(self):
        bucket_name = (settings.GCS_BUCKET_NAME or "").strip()
        if not bucket_name:
            raise RuntimeError("GCS storage is enabled, but GCS_BUCKET_NAME is not configured")

        if self._client is None:
            try:
                from google.auth.exceptions import DefaultCredentialsError
                from google.cloud import storage
            except ImportError as exc:
                raise RuntimeError(
                    "GCS storage is enabled, but google-cloud-storage is not installed"
                ) from exc

            try:
                self._client = storage.Client()
            except DefaultCredentialsError as exc:
                raise RuntimeError(
                    "GCS storage is enabled, but Google Cloud credentials are not configured"
                ) from exc
            except Exception as exc:
                raise RuntimeError(f"Failed to initialize Google Cloud Storage client: {exc}") from exc

        return self._client.bucket(bucket_name)

    def _generate_signed_url(self, object_path: str) -> str:
        ttl_minutes = settings.GCS_SIGNED_URL_EXPIRATION_MINUTES
        if ttl_minutes <= 0:
            ttl_minutes = 60
        logger.debug("[STORAGE] generating signed url for %s", object_path)
        blob = self._get_bucket().blob(object_path)
        expiration = timedelta(minutes=ttl_minutes)

        service_account_email = (settings.GCP_SERVICE_ACCOUNT_EMAIL or "").strip()
        if service_account_email:
            try:
                import google.auth
                from google.auth.transport.requests import Request
            except ImportError as exc:
                raise RuntimeError(
                    "GCS signed URLs require google-auth support, but the dependency is unavailable"
                ) from exc

            credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
            credentials.refresh(Request())
            return blob.generate_signed_url(
                expiration=expiration,
                method="GET",
                version="v4",
                service_account_email=service_account_email,
                access_token=credentials.token,
            )

        try:
            return blob.generate_signed_url(
                expiration=expiration,
                method="GET",
                version="v4",
            )
        except AttributeError as exc:
            raise RuntimeError("GCP_SERVICE_ACCOUNT_EMAIL is required for signed URLs on Cloud Run") from exc

    def _normalize_destination_path(self, destination_path: str) -> str:
        raw_path = str(destination_path or "").strip().lstrip("/")
        if not raw_path:
            raise RuntimeError("Storage destination path cannot be empty")
        prefix = self._normalized_media_prefix()
        if raw_path == "media" or raw_path.startswith("media/"):
            return raw_path

        if prefix and raw_path != prefix and not raw_path.startswith(f"{prefix}/"):
            return f"{prefix}/{raw_path}"
        return raw_path

    def _normalized_media_prefix(self) -> str:
        return str(settings.GCS_MEDIA_PREFIX or "").strip().strip("/")

    def _local_relative_path(self, storage_path: str) -> Path:
        prefix = self._normalized_media_prefix()
        relative_path = storage_path
        if prefix and (storage_path == prefix or storage_path.startswith(f"{prefix}/")):
            relative_path = storage_path[len(prefix) :].lstrip("/")
        return Path(relative_path)

    def _local_path_from_url(self, url: str) -> Path | None:
        parsed = urlparse(url)
        path = parsed.path if parsed.scheme or parsed.netloc else url
        normalized = str(path or "").strip()
        if not normalized.startswith("/media/"):
            return None
        relative_path = normalized.removeprefix("/media/").lstrip("/")
        if not relative_path:
            return None
        return self.media_root / Path(relative_path)

    def _is_gcs_not_found(self, exc: Exception) -> bool:
        try:
            from google.api_core.exceptions import NotFound
        except ImportError:
            NotFound = None

        if NotFound is not None and isinstance(exc, NotFound):
            return True
        return exc.__class__.__name__ == "NotFound"
