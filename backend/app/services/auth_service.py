from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import TokenResponse
from app.models.user import User


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register_user(self, email: str, password: str) -> User:
        existing_user = self.repo.get_user_by_email(email)
        if existing_user is not None:
            raise ValueError("Email already registered")

        hashed = hash_password(password)
        return self.repo.create_user(email, hashed)

    def login_user(self, email: str, password: str) -> TokenResponse:
        user = self.repo.get_user_by_email(email)
        if user is None:
            raise ValueError("Invalid credentials")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        token = create_access_token({"sub": str(user.id)})
        return TokenResponse(access_token=token, token_type="bearer")
