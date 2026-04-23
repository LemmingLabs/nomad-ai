from pathlib import Path
import sys
from unittest.mock import Mock

from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.models.user import User
from app.models.subscription_plan import BillingPeriod, SubscriptionPlan, SubscriptionPlanName
from app.repositories.user_repository import UserRepository


def test_get_user_by_email_returns_user_from_scalar_result() -> None:
    db = Mock(spec=Session)
    result = Mock()
    expected_user = User(email="traveler@example.com", password_hash="hashed-password")
    result.scalar_one_or_none.return_value = expected_user
    db.execute.return_value = result
    repository = UserRepository(db)

    user = repository.get_user_by_email("traveler@example.com")

    assert user is expected_user
    db.execute.assert_called_once()
    result.scalar_one_or_none.assert_called_once_with()


def test_get_user_by_email_returns_none_when_user_does_not_exist() -> None:
    db = Mock(spec=Session)
    result = Mock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result
    repository = UserRepository(db)

    user = repository.get_user_by_email("missing@example.com")

    assert user is None
    db.execute.assert_called_once()
    result.scalar_one_or_none.assert_called_once_with()


def test_get_user_by_id_uses_session_get() -> None:
    db = Mock(spec=Session)
    expected_user = User(email="traveler@example.com", password_hash="hashed-password")
    db.get.return_value = expected_user
    repository = UserRepository(db)

    user = repository.get_user_by_id(42)

    assert user is expected_user
    db.get.assert_called_once_with(User, 42)


def test_create_user_adds_commits_refreshes_and_returns_user() -> None:
    db = Mock(spec=Session)
    free_plan = SubscriptionPlan(
        name=SubscriptionPlanName.FREE,
        price=0.0,
        currency="USD",
        billing_period=BillingPeriod.FREE,
        trip_limit_per_day=3,
        chat_edit_limit_per_day=20,
        is_active=True,
    )
    result = Mock()
    result.scalar_one_or_none.return_value = free_plan
    db.execute.return_value = result
    repository = UserRepository(db)

    user = repository.create_user(
        email="newuser@example.com",
        password_hash="hashed-password",
    )

    assert isinstance(user, User)
    assert user.email == "newuser@example.com"
    assert user.password_hash == "hashed-password"
    db.add.assert_any_call(user)
    assert db.add.call_count == 2
    db.commit.assert_called_once_with()
    db.flush.assert_called_once_with()
    db.refresh.assert_called_once_with(user)
