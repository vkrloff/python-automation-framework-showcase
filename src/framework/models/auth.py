"""Login models (`/rest/user/login`)."""

from framework.models.base import ApiModel, ApiRequest, WireSecret


class LoginRequest(ApiRequest):
    email: str
    password: WireSecret


class Authentication(ApiModel):
    token: str
    bid: int
    """Basket id of the logged-in user."""
    umail: str


class LoginResponse(ApiModel):
    authentication: Authentication
