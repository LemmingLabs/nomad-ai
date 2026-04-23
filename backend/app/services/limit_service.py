from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.subscription_plan import SubscriptionPlan, SubscriptionPlanName
from app.services.subscription_service import SubscriptionService
from app.services.usage_service import UsageService


class LimitService:
    def __init__(
        self,
        db: Session,
        subscription_service: SubscriptionService | None = None,
        usage_service: UsageService | None = None,
    ):
        self.db = db
        self.subscriptions = subscription_service or SubscriptionService(db)
        self.usage = usage_service or UsageService(db)

    def _get_effective_plan(self, user_id: int) -> SubscriptionPlan | None:
        subscription = self.subscriptions.get_active_subscription(user_id)
        if subscription is not None and subscription.plan is not None:
            return subscription.plan

        statement = select(SubscriptionPlan).where(
            SubscriptionPlan.name == SubscriptionPlanName.FREE,
            SubscriptionPlan.is_active.is_(True),
        )
        return self.db.execute(statement).scalar_one_or_none()

    @staticmethod
    def _limit_allows(current: int, limit: int) -> bool:
        if limit <= 0:
            return False
        return current < limit

    def can_generate_trip(self, user_id: int) -> bool:
        plan = self._get_effective_plan(user_id)
        if plan is None:
            return False
        usage = self.usage.get_today_usage(user_id)
        used = usage.trip_generations_count if usage is not None else 0
        return self._limit_allows(
            current=used,
            limit=plan.trip_limit_per_day,
        )

    def can_edit_chat(self, user_id: int) -> bool:
        plan = self._get_effective_plan(user_id)
        if plan is None:
            return False
        usage = self.usage.get_today_usage(user_id)
        used = usage.chat_edits_count if usage is not None else 0
        return self._limit_allows(
            current=used,
            limit=plan.chat_edit_limit_per_day,
        )

    def get_limit_status(self, user_id: int) -> dict:
        subscription = self.subscriptions.get_active_subscription(user_id)
        plan = getattr(subscription, "plan", None) if subscription else None
        if plan is None:
            plan = self._get_effective_plan(user_id)

        usage = self.usage.get_today_usage(user_id)
        trip_used = usage.trip_generations_count if usage is not None else 0
        chat_used = usage.chat_edits_count if usage is not None else 0

        plan_name = getattr(plan, "name", None)
        if plan_name is not None:
            plan_name = str(plan_name.value) if hasattr(plan_name, "value") else str(plan_name)

        return {
            "plan": plan_name,
            "trip_limit_per_day": getattr(plan, "trip_limit_per_day", 0) if plan else 0,
            "trip_generations_used": trip_used,
            "chat_edit_limit_per_day": getattr(plan, "chat_edit_limit_per_day", 0) if plan else 0,
            "chat_edits_used": chat_used,
        }
