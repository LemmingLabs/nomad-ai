from datetime import datetime, timezone
from pathlib import Path
import sys
from unittest.mock import Mock, patch

import pytest
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from fastapi import HTTPException
from jose import jwt
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.dependencies import get_current_user, oauth2_scheme
from app.core import security
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService


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


def test_auth_service_register_user_raises_when_email_already_registered() -> None:
    existing_user = Mock()

    with patch("app.services.auth_service.UserRepository") as repository_class:
        repository_class.return_value.get_user_by_email.return_value = existing_user
        service = AuthService(Mock())

        with pytest.raises(ValueError, match="Email already registered"):
            service.register_user("traveler@example.com", "secret123")

        repository_class.return_value.get_user_by_email.assert_called_once_with(
            "traveler@example.com"
        )


def test_auth_service_register_user_hashes_password_and_creates_user() -> None:
    created_user = Mock()

    with (
        patch("app.services.auth_service.UserRepository") as repository_class,
        patch("app.services.auth_service.hash_password") as mock_hash_password,
    ):
        repository = repository_class.return_value
        repository.get_user_by_email.return_value = None
        repository.create_user.return_value = created_user
        mock_hash_password.return_value = "hashed-password"
        service = AuthService(Mock())

        user = service.register_user("traveler@example.com", "secret123")

        assert user is created_user
        repository.get_user_by_email.assert_called_once_with("traveler@example.com")
        mock_hash_password.assert_called_once_with("secret123")
        repository.create_user.assert_called_once_with(
            "traveler@example.com", "hashed-password"
        )


def test_auth_service_login_user_raises_when_user_does_not_exist() -> None:
    with patch("app.services.auth_service.UserRepository") as repository_class:
        repository_class.return_value.get_user_by_email.return_value = None
        service = AuthService(Mock())

        with pytest.raises(ValueError, match="Invalid credentials"):
            service.login_user("traveler@example.com", "secret123")

        repository_class.return_value.get_user_by_email.assert_called_once_with(
            "traveler@example.com"
        )


def test_auth_service_login_user_raises_when_password_is_invalid() -> None:
    user = Mock()
    user.password_hash = "stored-hash"

    with (
        patch("app.services.auth_service.UserRepository") as repository_class,
        patch("app.services.auth_service.verify_password") as mock_verify_password,
    ):
        repository = repository_class.return_value
        repository.get_user_by_email.return_value = user
        mock_verify_password.return_value = False
        service = AuthService(Mock())

        with pytest.raises(ValueError, match="Invalid credentials"):
            service.login_user("traveler@example.com", "wrong-password")

        repository.get_user_by_email.assert_called_once_with("traveler@example.com")
        mock_verify_password.assert_called_once_with(
            "wrong-password", "stored-hash"
        )


def test_auth_service_login_user_returns_bearer_token_for_valid_credentials() -> None:
    user = Mock()
    user.id = 7
    user.password_hash = "stored-hash"

    with (
        patch("app.services.auth_service.UserRepository") as repository_class,
        patch("app.services.auth_service.verify_password") as mock_verify_password,
        patch("app.services.auth_service.create_access_token") as mock_create_access_token,
    ):
        repository = repository_class.return_value
        repository.get_user_by_email.return_value = user
        mock_verify_password.return_value = True
        mock_create_access_token.return_value = "jwt-token"
        service = AuthService(Mock())

        token_response = service.login_user("traveler@example.com", "secret123")

        assert token_response == TokenResponse(
            access_token="jwt-token",
            token_type="bearer",
        )
        repository.get_user_by_email.assert_called_once_with("traveler@example.com")
        mock_verify_password.assert_called_once_with("secret123", "stored-hash")
        mock_create_access_token.assert_called_once_with({"sub": "7"})


def test_oauth2_scheme_uses_login_token_url() -> None:
    assert oauth2_scheme.model.flows.password.tokenUrl == "/api/v1/auth/login"


@pytest.mark.asyncio
async def test_get_current_user_raises_401_when_token_cannot_be_decoded() -> None:
    with patch("app.core.dependencies.decode_access_token") as mock_decode_access_token:
        mock_decode_access_token.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token="bad-token", db=Mock())

        assert exc_info.value.status_code == 401
        mock_decode_access_token.assert_called_once_with("bad-token")


@pytest.mark.asyncio
async def test_get_current_user_raises_401_when_sub_claim_is_missing() -> None:
    with patch("app.core.dependencies.decode_access_token") as mock_decode_access_token:
        mock_decode_access_token.return_value = {}

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token="token-without-sub", db=Mock())

        assert exc_info.value.status_code == 401
        mock_decode_access_token.assert_called_once_with("token-without-sub")


@pytest.mark.asyncio
async def test_get_current_user_raises_401_when_sub_claim_is_not_an_int() -> None:
    with patch("app.core.dependencies.decode_access_token") as mock_decode_access_token:
        mock_decode_access_token.return_value = {"sub": "not-an-int"}

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token="token-with-invalid-sub", db=Mock())

        assert exc_info.value.status_code == 401
        mock_decode_access_token.assert_called_once_with("token-with-invalid-sub")


@pytest.mark.asyncio
async def test_get_current_user_raises_401_when_user_does_not_exist() -> None:
    with (
        patch("app.core.dependencies.decode_access_token") as mock_decode_access_token,
        patch("app.core.dependencies.UserRepository") as repository_class,
    ):
        mock_decode_access_token.return_value = {"sub": "7"}
        repository_class.return_value.get_user_by_id.return_value = None
        db = Mock()

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token="valid-token", db=db)

        assert exc_info.value.status_code == 401
        mock_decode_access_token.assert_called_once_with("valid-token")
        repository_class.assert_called_once_with(db)
        repository_class.return_value.get_user_by_id.assert_called_once_with(7)


@pytest.mark.asyncio
async def test_get_current_user_returns_user_for_valid_token() -> None:
    user = Mock()

    with (
        patch("app.core.dependencies.decode_access_token") as mock_decode_access_token,
        patch("app.core.dependencies.UserRepository") as repository_class,
    ):
        mock_decode_access_token.return_value = {"sub": "7"}
        repository_class.return_value.get_user_by_id.return_value = user
        db = Mock()

        current_user = await get_current_user(token="valid-token", db=db)

        assert current_user is user
        mock_decode_access_token.assert_called_once_with("valid-token")
        repository_class.assert_called_once_with(db)
        repository_class.return_value.get_user_by_id.assert_called_once_with(7)
