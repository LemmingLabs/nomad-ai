from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.subscription import (
    LimitStatusResponse,
    MockPurchaseSubscriptionRequest,
    SubscriptionMeResponse,
    SubscriptionPlanResponse,
    UserSubscriptionResponse,
)
from app.services.limit_service import LimitService
from app.services.subscription_service import SubscriptionService


router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/plans", response_model=list[SubscriptionPlanResponse])
def list_active_plans(
    db: Session = Depends(get_db),
) -> list[SubscriptionPlanResponse]:
    plans = SubscriptionService(db).list_active_plans()
    return [SubscriptionPlanResponse.model_validate(plan) for plan in plans]


@router.get("/me", response_model=SubscriptionMeResponse)
def get_my_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubscriptionMeResponse:
    subscription = SubscriptionService(db).get_user_active_subscription(current_user.id)
    if subscription is None:
        return SubscriptionMeResponse(subscription=None)
    return SubscriptionMeResponse(subscription=UserSubscriptionResponse.model_validate(subscription))


@router.get("/me/limits", response_model=LimitStatusResponse)
def get_my_limits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LimitStatusResponse:
    status_data = LimitService(db).get_limit_status(current_user.id)
    return LimitStatusResponse(**status_data)


@router.post(
    "/mock-purchase",
    response_model=UserSubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def mock_purchase_subscription(
    payload: MockPurchaseSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserSubscriptionResponse:
    try:
        subscription = SubscriptionService(db).mock_purchase_subscription(
            user_id=current_user.id,
            plan_id=payload.plan_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return UserSubscriptionResponse.model_validate(subscription)

