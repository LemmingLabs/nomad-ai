from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository


class AdminUserService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def list_users(self, limit: int = 50, offset: int = 0) -> list[User]:
        return self.users.list_users(limit=limit, offset=offset)

    def get_user(self, user_id: int) -> User:
        user = self.users.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def update_user_role(
        self,
        user_id: int,
        role: UserRole,
        current_admin_user_id: int,
    ) -> User:
        user = self.get_user(user_id)

        if user.id == current_admin_user_id and role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin cannot change own role",
            )

        if user.role == UserRole.ADMIN and role != UserRole.ADMIN:
            admin_count = self.users.count_admins()
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove role from the last admin",
                )

        if user.role == role:
            return user

        return self.users.update_user_role(user, role)

