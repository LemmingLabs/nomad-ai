from app.core.config import settings
from app.services.storage_service import StorageService


class _FakeBlob:
    def __init__(self, name: str):
        self.name = name
        self.uploaded = None
        self.deleted = False
        self.cache_control = None
        self.patched = False

    def upload_from_string(self, content: bytes, content_type: str) -> None:
        self.uploaded = (content, content_type)

    def delete(self) -> None:
        self.deleted = True

    def patch(self) -> None:
        self.patched = True

    def generate_signed_url(self, expiration, method: str, version: str) -> str:
        return f"https://signed.example.com/{self.name}?method={method}&version={version}&ttl={expiration.total_seconds()}"


class _FakeBucket:
    def __init__(self):
        self.blobs: dict[str, _FakeBlob] = {}

    def blob(self, name: str) -> _FakeBlob:
        blob = self.blobs.get(name)
        if blob is None:
            blob = _FakeBlob(name)
            self.blobs[name] = blob
        return blob


def test_storage_service_uploads_and_deletes_local_files(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")

    service = StorageService()
    service.media_root = tmp_path

    url = service.upload_bytes(
        b"image-bytes",
        destination_path="media/businesses/12/sponsored_places/34/photo.jpg",
        content_type="image/jpeg",
    )

    assert url == "/media/businesses/12/sponsored_places/34/photo.jpg"
    stored_file = tmp_path / "businesses" / "12" / "sponsored_places" / "34" / "photo.jpg"
    assert stored_file.read_bytes() == b"image-bytes"
    assert service.get_access_url(url) == url

    service.delete(url)

    assert stored_file.exists() is False


def test_storage_service_uploads_signs_and_deletes_gcs_objects(monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "gcs")
    monkeypatch.setattr(settings, "GCS_BUCKET_NAME", "nomadai-bucket")
    monkeypatch.setattr(settings, "GCS_MEDIA_PREFIX", "media")
    monkeypatch.setattr(settings, "GCS_SIGNED_URL_EXPIRATION_MINUTES", 60)

    fake_bucket = _FakeBucket()
    service = StorageService()
    monkeypatch.setattr(service, "_get_bucket", lambda: fake_bucket)

    stored_key = service.upload_bytes(
        b"gcs-bytes",
        destination_path="media/businesses/7/sponsored_places/9/cover.webp",
        content_type="image/webp",
    )

    assert stored_key == "media/businesses/7/sponsored_places/9/cover.webp"
    blob = fake_bucket.blobs[stored_key]
    assert blob.uploaded == (b"gcs-bytes", "image/webp")
    assert blob.cache_control == "private, max-age=31536000"
    assert blob.patched is True

    signed_url = service.get_access_url(stored_key)

    assert signed_url.startswith("https://signed.example.com/media/businesses/7/sponsored_places/9/cover.webp")
    assert service.get_access_url("https://cdn.example.com/already-signed") == "https://cdn.example.com/already-signed"

    service.delete(signed_url)

    assert blob.deleted is True
