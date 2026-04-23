from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.user import UserRole


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: UserRole
    created_at: datetime


class AdminUserRoleUpdateRequest(BaseModel):
    role: UserRole

