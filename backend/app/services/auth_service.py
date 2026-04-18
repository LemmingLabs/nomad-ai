from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import TokenResponse
from app.models.user import User

DUMMY_HASH = hash_password("dummy")  # module-level constant, computed once at startup

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
        
        # Always run verify_password to prevent timing-based email enumeration
        # If user doesn't exist, verify against a dummy hash so response time is constant
        password_hash = user.password_hash if user else DUMMY_HASH
        password_ok = verify_password(password, password_hash)
        
        if not user or not password_ok:
            raise ValueError("Invalid credentials")

        token = create_access_token({"sub": str(user.id)})
        return TokenResponse(access_token=token, token_type="bearer")
