from datetime import datetime, timezone
from pathlib import Path
import sys
from unittest.mock import Mock

import pytest
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from jose import jwt
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core import security
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


def test_hash_password_delegates_to_argon2_password_hasher(monkeypatch: pytest.MonkeyPatch) -> None:
    password = "nomad-secure-password"
    password_hasher = Mock()
    password_hasher.hash.return_value = "argon2-hash"

    monkeypatch.setattr(security, "password_hasher", password_hasher)

    hashed_password = security.hash_password(password)

    assert hashed_password == "argon2-hash"
    password_hasher.hash.assert_called_once_with(password)


def test_verify_password_returns_false_for_wrong_password(monkeypatch: pytest.MonkeyPatch) -> None:
    password_hasher = Mock()
    password_hasher.verify.side_effect = VerifyMismatchError

    monkeypatch.setattr(security, "password_hasher", password_hasher)

    result = security.verify_password("wrong-password", "stored-hash")

    assert result is False
    password_hasher.verify.assert_called_once_with("stored-hash", "wrong-password")


def test_verify_password_returns_false_for_invalid_hash(monkeypatch: pytest.MonkeyPatch) -> None:
    password_hasher = Mock()
    password_hasher.verify.side_effect = InvalidHashError

    monkeypatch.setattr(security, "password_hasher", password_hasher)

    assert security.verify_password("password", "not-a-valid-argon2-hash") is False
    password_hasher.verify.assert_called_once_with(
        "not-a-valid-argon2-hash", "password"
    )


def test_verify_password_checks_needs_rehash_after_success(monkeypatch: pytest.MonkeyPatch) -> None:
    password_hasher = Mock()
    password_hasher.verify.return_value = True
    password_hasher.check_needs_rehash.return_value = False

    monkeypatch.setattr(security, "password_hasher", password_hasher)

    assert security.verify_password("correct-password", "stored-hash") is True
    password_hasher.verify.assert_called_once_with("stored-hash", "correct-password")
    password_hasher.check_needs_rehash.assert_called_once_with("stored-hash")


def test_create_access_token_adds_exp_and_does_not_mutate_input(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(security.settings, "JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setattr(security.settings, "JWT_ALGORITHM", "HS256")
    monkeypatch.setattr(security.settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 15)
    payload = {"sub": "traveler@example.com"}

    token = security.create_access_token(payload)
    decoded = jwt.decode(
        token,
        security.settings.JWT_SECRET_KEY,
        algorithms=[security.settings.JWT_ALGORITHM],
    )

    assert "exp" not in payload
    assert decoded["sub"] == "traveler@example.com"
    assert "exp" in decoded


def test_decode_access_token_returns_payload_for_valid_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(security.settings, "JWT_SECRET_KEY", "decode-secret-key")
    monkeypatch.setattr(security.settings, "JWT_ALGORITHM", "HS256")
    token = jwt.encode(
        {"sub": "valid-user@example.com"},
        security.settings.JWT_SECRET_KEY,
        algorithm=security.settings.JWT_ALGORITHM,
    )

    decoded = security.decode_access_token(token)

    assert decoded is not None
    assert decoded["sub"] == "valid-user@example.com"


def test_decode_access_token_returns_none_for_invalid_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(security.settings, "JWT_SECRET_KEY", "invalid-secret-key")
    monkeypatch.setattr(security.settings, "JWT_ALGORITHM", "HS256")

    assert security.decode_access_token("not-a-jwt") is None


def test_decode_access_token_returns_none_for_expired_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(security.settings, "JWT_SECRET_KEY", "expired-secret-key")
    monkeypatch.setattr(security.settings, "JWT_ALGORITHM", "HS256")
    expired_token = jwt.encode(
        {
            "sub": "expired-user@example.com",
            "exp": datetime.now(timezone.utc).timestamp() - 60,
        },
        security.settings.JWT_SECRET_KEY,
        algorithm=security.settings.JWT_ALGORITHM,
    )

    assert security.decode_access_token(expired_token) is None
