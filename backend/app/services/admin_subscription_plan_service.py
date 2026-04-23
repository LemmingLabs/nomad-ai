from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.subscription_plan import SubscriptionPlan
from app.repositories.subscription_plan_repository import SubscriptionPlanRepository


class AdminSubscriptionPlanService:
    def __init__(self, db: Session):
        self.db = db
        self.plans = SubscriptionPlanRepository(db)

    def list_all_plans(self, *, limit: int = 200, offset: int = 0) -> list[SubscriptionPlan]:
        return self.plans.list_all(limit=limit, offset=offset)

    def get_plan(self, plan_id: int) -> SubscriptionPlan:
        plan = self.plans.get_by_id(plan_id)
        if plan is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription plan not found")
        return plan

    def create_plan(
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
        try:
            plan = self.plans.create(
                name=name,
                price=price,
                currency=currency,
                billing_period=billing_period,
                trip_limit_per_day=trip_limit_per_day,
                chat_edit_limit_per_day=chat_edit_limit_per_day,
                is_active=is_active,
            )
            self.db.commit()
            self.db.refresh(plan)
            return plan
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription plan with this name already exists",
            ) from exc

    def update_plan(self, plan_id: int, **updates) -> SubscriptionPlan:
        plan = self.get_plan(plan_id)
        plan = self.plans.update(plan, **updates)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def activate_plan(self, plan_id: int) -> SubscriptionPlan:
        return self.update_plan(plan_id, is_active=True)

    def deactivate_plan(self, plan_id: int) -> SubscriptionPlan:
        return self.update_plan(plan_id, is_active=False)

