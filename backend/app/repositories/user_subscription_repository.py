from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.user_subscription import UserSubscription, UserSubscriptionStatus


class UserSubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_for_user(self, user_id: int) -> UserSubscription | None:
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

    def cancel_active_for_user(self, user_id: int) -> int:
        now = datetime.now(timezone.utc)
        statement = (
            select(UserSubscription)
            .where(
                UserSubscription.user_id == user_id,
                UserSubscription.status == UserSubscriptionStatus.ACTIVE,
                or_(
                    UserSubscription.expires_at.is_(None),
                    UserSubscription.expires_at > now,
                ),
            )
            .order_by(UserSubscription.started_at.desc())
        )
        subs = list(self.db.execute(statement).scalars().all())
        count = 0
        for sub in subs:
            sub.status = UserSubscriptionStatus.CANCELED
            sub.expires_at = now
            self.db.add(sub)
            count += 1
        self.db.flush()
        return count

    def create(
        self,
        *,
        user_id: int,
        plan_id: int,
        status: UserSubscriptionStatus,
        started_at: datetime,
        expires_at: datetime | None,
    ) -> UserSubscription:
        subscription = UserSubscription(
            user_id=user_id,
            plan_id=plan_id,
            status=status,
            started_at=started_at,
            expires_at=expires_at,
        )
        self.db.add(subscription)
        self.db.flush()
        return subscription

