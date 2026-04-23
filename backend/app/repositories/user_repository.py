from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.subscription_plan import BillingPeriod, SubscriptionPlan, SubscriptionPlanName
from app.models.user_subscription import UserSubscription, UserSubscriptionStatus
from app.models.user import User, UserRole


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.db.execute(statement).scalar_one_or_none()

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def list_users(self, *, limit: int = 50, offset: int = 0) -> list[User]:
        statement = (
            select(User)
            .order_by(User.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.execute(statement).scalars().all())

    def count_admins(self) -> int:
        statement = select(func.count(User.id)).where(User.role == UserRole.ADMIN)
        return int(self.db.execute(statement).scalar() or 0)

    def update_user_role(self, user: User, role: UserRole) -> User:
        user.role = role
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def _get_or_create_free_plan(self) -> SubscriptionPlan:
        statement = select(SubscriptionPlan).where(
            SubscriptionPlan.name == SubscriptionPlanName.FREE
        )
        plan = self.db.execute(statement).scalar_one_or_none()
        if plan is not None:
            return plan

        plan = SubscriptionPlan(
            name=SubscriptionPlanName.FREE,
            price=0.0,
            currency="USD",
            billing_period=BillingPeriod.FREE,
            trip_limit_per_day=3,
            chat_edit_limit_per_day=20,
            is_active=True,
        )
        self.db.add(plan)
        self.db.flush()
        return plan

    def create_user(self, email: str, password_hash: str) -> User:
        user = User(email=email, password_hash=password_hash)
        self.db.add(user)
        self.db.flush()

        free_plan = self._get_or_create_free_plan()
        subscription = UserSubscription(
            user=user,
            plan=free_plan,
            status=UserSubscriptionStatus.ACTIVE,
            started_at=datetime.now(timezone.utc),
            expires_at=None,
        )
        self.db.add(subscription)

        self.db.commit()
        self.db.refresh(user)
        return user
