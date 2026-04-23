from __future__ import annotations

from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.core.security import hash_password, verify_password  # noqa: E402
from app.models.user import UserRole  # noqa: E402
from app.repositories.user_repository import UserRepository  # noqa: E402


def _require_non_empty(value: str | None, name: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        raise ValueError(f"{name} is required")
    return cleaned


def ensure_admin_user(db: Session) -> str:
    admin_email = _require_non_empty(settings.ADMIN_EMAIL, "ADMIN_EMAIL")
    admin_password = _require_non_empty(settings.ADMIN_PASSWORD, "ADMIN_PASSWORD")

    repo = UserRepository(db)
    user = repo.get_user_by_email(admin_email)

    if user is None:
        user = repo.create_user(
            email=admin_email,
            password_hash=hash_password(admin_password),
        )
        user.role = UserRole.ADMIN
        db.add(user)
        db.commit()
        return f"created: {admin_email}"

    changed = False

    if user.role != UserRole.ADMIN:
        user.role = UserRole.ADMIN
        changed = True

    if not verify_password(admin_password, user.password_hash):
        user.password_hash = hash_password(admin_password)
        changed = True

    if changed:
        db.add(user)
        db.commit()
        return f"updated: {admin_email}"

    return f"skipped: {admin_email}"


def main() -> None:
    db = SessionLocal()
    try:
        result = ensure_admin_user(db)
    finally:
        db.close()
    print(result)


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(f"error: {exc}")
        raise SystemExit(1) from exc
