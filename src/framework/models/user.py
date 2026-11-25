"""User registration and identity models (`/api/Users`, `/rest/user/whoami`)."""

from typing import Literal

from pydantic import field_validator

from framework.models.base import ApiModel, ApiRequest, WireSecret


class RegisterRequest(ApiRequest):
    email: str
    password: WireSecret
    password_repeat: WireSecret


class RegisteredUser(ApiModel):
    id: int
    email: str
    role: str


class RegisterResponse(ApiModel):
    status: Literal["success"]
    data: RegisteredUser


class WhoAmIUser(ApiModel):
    id: int
    email: str


class WhoAmIResponse(ApiModel):
    """`user` is `{}` for an anonymous caller; that is mapped to `None`."""

    user: WhoAmIUser | None

    @field_validator("user", mode="before")
    @classmethod
    def _empty_object_is_anonymous(cls, value: object) -> object:
        return None if value == {} else value
