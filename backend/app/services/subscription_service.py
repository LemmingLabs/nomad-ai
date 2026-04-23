from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.user_subscription import UserSubscription, UserSubscriptionStatus


class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db

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


def get_active_subscription(db: Session, user_id: int) -> UserSubscription | None:
    return SubscriptionService(db).get_active_subscription(user_id)
