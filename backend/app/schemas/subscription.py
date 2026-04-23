from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.subscription_plan import BillingPeriod, SubscriptionPlanName
from app.models.user_subscription import UserSubscriptionStatus


class SubscriptionPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: SubscriptionPlanName
    price: float
    currency: str
    billing_period: BillingPeriod
    trip_limit_per_day: int
    chat_edit_limit_per_day: int
    is_active: bool


class UserSubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    plan_id: int
    status: UserSubscriptionStatus
    started_at: datetime
    expires_at: datetime | None
    plan: SubscriptionPlanResponse


class SubscriptionMeResponse(BaseModel):
    subscription: UserSubscriptionResponse | None


class LimitStatusResponse(BaseModel):
    plan: str | None = None
    trip_limit_per_day: int
    trip_generations_used: int
    chat_edit_limit_per_day: int
    chat_edits_used: int


class MockPurchaseSubscriptionRequest(BaseModel):
    plan_id: int = Field(gt=0)


class AdminSubscriptionPlanCreateRequest(BaseModel):
    name: SubscriptionPlanName
    price: float = Field(ge=0)
    currency: str = Field(min_length=1, max_length=10, default="USD")
    billing_period: BillingPeriod
    trip_limit_per_day: int = Field(ge=0)
    chat_edit_limit_per_day: int = Field(ge=0)
    is_active: bool = True


class AdminSubscriptionPlanUpdateRequest(BaseModel):
    name: SubscriptionPlanName | None = None
    price: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=1, max_length=10)
    billing_period: BillingPeriod | None = None
    trip_limit_per_day: int | None = Field(default=None, ge=0)
    chat_edit_limit_per_day: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

