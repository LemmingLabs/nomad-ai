from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.subscription_plan import BillingPeriod, SubscriptionPlan
from app.repositories.subscription_plan_repository import SubscriptionPlanRepository
from app.repositories.user_subscription_repository import UserSubscriptionRepository
from app.models.user_subscription import UserSubscription, UserSubscriptionStatus


class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db
        self.plan_repo = SubscriptionPlanRepository(db)
        self.sub_repo = UserSubscriptionRepository(db)

    def get_active_subscription(self, user_id: int) -> UserSubscription | None:
        now = datetime.now(timezone.utc)
        statement = (
            select(UserSubscription)
            .options(joinedload(UserSubscription.plan))
            .where(
                UserSubscription.user_id == user_id,
                UserSubscription.status == UserSubscriptionStatus.ACTIVE,
                or_(
                    UserSubscription.expires_at.is_(None),
                    UserSubscription.expires_at > now,
                ),
            )
            .order_by(UserSubscription.started_at.desc())
            .limit(1)
        )
        return self.db.execute(statement).scalar_one_or_none()

    def list_active_plans(self) -> list[SubscriptionPlan]:
        return self.plan_repo.list_active()

    def get_user_active_subscription(self, user_id: int) -> UserSubscription | None:
        return self.sub_repo.get_active_for_user(user_id)

    @staticmethod
    def _calculate_expires_at(billing_period: BillingPeriod, now: datetime) -> datetime | None:
        if billing_period in {BillingPeriod.FREE, BillingPeriod.LIFETIME}:
            return None
        if billing_period == BillingPeriod.MONTHLY:
            return now + timedelta(days=30)
        if billing_period == BillingPeriod.YEARLY:
            return now + timedelta(days=365)
        return None

    def mock_purchase_subscription(self, *, user_id: int, plan_id: int) -> UserSubscription:
        plan = self.plan_repo.get_by_id(plan_id)
        if plan is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription plan not found")
        if not plan.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan is not active")

        current = self.sub_repo.get_active_for_user(user_id)
        if current is not None and current.plan_id == plan_id:
            return current

        now = datetime.now(timezone.utc)
        self.sub_repo.cancel_active_for_user(user_id)
        expires_at = self._calculate_expires_at(plan.billing_period, now)
        subscription = self.sub_repo.create(
            user_id=user_id,
            plan_id=plan_id,
            status=UserSubscriptionStatus.ACTIVE,
            started_at=now,
            expires_at=expires_at,
        )
        self.db.commit()
        # reload with joined plan
        reloaded = self.sub_repo.get_active_for_user(user_id)
        if reloaded is not None and reloaded.id == subscription.id:
            return reloaded
        self.db.refresh(subscription)
        return subscription


def get_active_subscription(db: Session, user_id: int) -> UserSubscription | None:
    return SubscriptionService(db).get_active_subscription(user_id)
