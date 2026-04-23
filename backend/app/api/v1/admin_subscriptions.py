from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.subscription import (
    AdminSubscriptionPlanCreateRequest,
    AdminSubscriptionPlanUpdateRequest,
    SubscriptionPlanResponse,
)
from app.services.admin_subscription_plan_service import AdminSubscriptionPlanService


router = APIRouter(prefix="/admin/subscription-plans", tags=["admin"])


@router.get("", response_model=list[SubscriptionPlanResponse])
def list_subscription_plans(
    limit: int = 200,
    offset: int = 0,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[SubscriptionPlanResponse]:
    plans = AdminSubscriptionPlanService(db).list_all_plans(limit=limit, offset=offset)
    return [SubscriptionPlanResponse.model_validate(plan) for plan in plans]


@router.post("", response_model=SubscriptionPlanResponse)
def create_subscription_plan(
    payload: AdminSubscriptionPlanCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> SubscriptionPlanResponse:
    plan = AdminSubscriptionPlanService(db).create_plan(
        name=payload.name,
        price=payload.price,
        currency=payload.currency,
        billing_period=payload.billing_period,
        trip_limit_per_day=payload.trip_limit_per_day,
        chat_edit_limit_per_day=payload.chat_edit_limit_per_day,
        is_active=payload.is_active,
    )
    return SubscriptionPlanResponse.model_validate(plan)


@router.patch("/{plan_id}", response_model=SubscriptionPlanResponse)
def update_subscription_plan(
    plan_id: int,
    payload: AdminSubscriptionPlanUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> SubscriptionPlanResponse:
    updates = payload.model_dump(exclude_unset=True)
    plan = AdminSubscriptionPlanService(db).update_plan(plan_id, **updates)
    return SubscriptionPlanResponse.model_validate(plan)


@router.patch("/{plan_id}/activate", response_model=SubscriptionPlanResponse)
def activate_subscription_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> SubscriptionPlanResponse:
    plan = AdminSubscriptionPlanService(db).activate_plan(plan_id)
    return SubscriptionPlanResponse.model_validate(plan)


@router.patch("/{plan_id}/deactivate", response_model=SubscriptionPlanResponse)
def deactivate_subscription_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> SubscriptionPlanResponse:
    plan = AdminSubscriptionPlanService(db).deactivate_plan(plan_id)
    return SubscriptionPlanResponse.model_validate(plan)

