from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse


def test_register_request_accepts_valid_email_and_password() -> None:
    payload = RegisterRequest(email="traveler@example.com", password="secret123")

    assert payload.email == "traveler@example.com"
    assert payload.password == "secret123"


def test_login_request_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(email="not-an-email", password="secret123")


def test_token_response_defaults_token_type_to_bearer() -> None:
    token = TokenResponse(access_token="jwt-token")

    assert token.access_token == "jwt-token"
    assert token.token_type == "bearer"


def test_user_response_builds_from_attributes_without_exposing_password_hash() -> None:
    created_at = datetime(2026, 4, 17, tzinfo=timezone.utc)

    class UserORM:
        def __init__(self) -> None:
            self.id = 7
            self.email = "nomad@example.com"
            self.created_at = created_at
            self.password_hash = "hidden"

    response = UserResponse.model_validate(UserORM())

    assert response.id == 7
    assert response.email == "nomad@example.com"
    assert response.created_at == created_at
    assert "password_hash" not in response.model_dump()
