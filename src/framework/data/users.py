"""Factory for unique, randomised test users."""

import secrets
from typing import ClassVar
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, SecretStr

from framework.models import LoginRequest, RegisterRequest


class UserCredentials(BaseModel):
    model_config = ConfigDict(frozen=True)

    email: str
    password: SecretStr

    def to_register_request(self) -> RegisterRequest:
        return RegisterRequest(
            email=self.email, password=self.password, password_repeat=self.password
        )

    def to_login_request(self) -> LoginRequest:
        return LoginRequest(email=self.email, password=self.password)


class RegisteredAccount(BaseModel):
    """A user that exists in the SUT: its id plus the credentials it was registered with."""

    model_config = ConfigDict(frozen=True)

    id: int
    credentials: UserCredentials


class UserFactory:
    EMAIL_DOMAIN: ClassVar[str] = "juice-sh.op"

    @classmethod
    def build(cls, *, email: str | None = None, password: str | None = None) -> UserCredentials:
        """Build credentials that are unique per call (safe for parallel runs)."""
        return UserCredentials(
            email=email if email is not None else f"qa_{uuid4().hex}@{cls.EMAIL_DOMAIN}",
            password=SecretStr(password if password is not None else cls._random_password()),
        )

    @staticmethod
    def _random_password() -> str:
        # Random part plus a fixed suffix that covers upper, lower, digit and symbol rules.
        return f"{secrets.token_urlsafe(12)}Aa1!"
