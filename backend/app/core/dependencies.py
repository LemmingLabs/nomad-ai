from fastapi import HTTPException, status

from app.models.user import User


def get_current_user() -> User:
    """Authentication stub for endpoints that require a logged-in user.

    Tests can override this dependency with app.dependency_overrides.
    """
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )
