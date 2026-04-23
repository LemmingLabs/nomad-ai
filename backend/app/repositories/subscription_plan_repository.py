from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.subscription_plan import SubscriptionPlan


class SubscriptionPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, plan_id: int) -> SubscriptionPlan | None:
        return self.db.get(SubscriptionPlan, plan_id)

    def list_active(self) -> list[SubscriptionPlan]:
        statement = (
            select(SubscriptionPlan)
            .where(SubscriptionPlan.is_active.is_(True))
            .order_by(SubscriptionPlan.price.asc(), SubscriptionPlan.created_at.asc())
        )
        return list(self.db.execute(statement).scalars().all())

    def list_all(self, *, limit: int = 200, offset: int = 0) -> list[SubscriptionPlan]:
        statement = (
            select(SubscriptionPlan)
            .order_by(SubscriptionPlan.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.execute(statement).scalars().all())

    def create(
        self,
        *,
        name,
        price: float,
        currency: str,
        billing_period,
        trip_limit_per_day: int,
        chat_edit_limit_per_day: int,
        is_active: bool,
    ) -> SubscriptionPlan:
        plan = SubscriptionPlan(
            name=name,
            price=price,
            currency=currency,
            billing_period=billing_period,
            trip_limit_per_day=trip_limit_per_day,
            chat_edit_limit_per_day=chat_edit_limit_per_day,
            is_active=is_active,
        )
        self.db.add(plan)
        self.db.flush()
        return plan

    def update(self, plan: SubscriptionPlan, **updates) -> SubscriptionPlan:
        for key, value in updates.items():
            setattr(plan, key, value)
        self.db.add(plan)
        self.db.flush()
        return plan

