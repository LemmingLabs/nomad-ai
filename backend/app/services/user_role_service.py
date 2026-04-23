from app.models.user import User, UserRole


def user_is_admin(user: User) -> bool:
    return user.role == UserRole.ADMIN


def user_is_business(user: User) -> bool:
    return user.role == UserRole.BUSINESS


def user_has_any_role(user: User, roles: set[UserRole]) -> bool:
    return user.role in roles

