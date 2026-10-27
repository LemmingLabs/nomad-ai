import pytest
from fastapi import HTTPException

from app.api.v1.subscriptions import mock_purchase_subscription
from app.core.config import settings
from app.schemas.subscription import MockPurchaseSubscriptionRequest


def test_mock_purchase_route_is_not_available_outside_development(monkeypatch):
    monkeypatch.setattr(settings, "APP_ENV", "production")

    with pytest.raises(HTTPException) as exception:
        mock_purchase_subscription(
            MockPurchaseSubscriptionRequest(plan_id=1),
            db=None,
            current_user=None,
        )

    assert exception.value.status_code == 404
    assert exception.value.detail == "Not found"
