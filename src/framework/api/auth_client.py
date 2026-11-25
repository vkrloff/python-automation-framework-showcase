"""Registration, login and identity endpoints."""

from requests import Response

from framework.api.base_client import BaseApiClient
from framework.models import (
    Authentication,
    LoginRequest,
    LoginResponse,
    RegisteredUser,
    RegisterRequest,
    RegisterResponse,
    WhoAmIResponse,
    WhoAmIUser,
)


class AuthClient(BaseApiClient):
    REGISTER_PATH = "/api/Users"
    LOGIN_PATH = "/rest/user/login"
    WHOAMI_PATH = "/rest/user/whoami"

    def register_raw(self, payload: RegisterRequest) -> Response:
        return self.request("POST", self.REGISTER_PATH, body=payload)

    def register(self, payload: RegisterRequest) -> RegisteredUser:
        return self.parse(self.register_raw(payload), RegisterResponse).data

    def login_raw(self, payload: LoginRequest) -> Response:
        return self.request("POST", self.LOGIN_PATH, body=payload)

    def login(self, payload: LoginRequest) -> Authentication:
        """Log in and return the token data. Does not authenticate this client."""
        return self.parse(self.login_raw(payload), LoginResponse).authentication

    def whoami(self) -> WhoAmIUser | None:
        """Return the user the session is authenticated as, or `None` if anonymous."""
        return self.parse(self.request("GET", self.WHOAMI_PATH), WhoAmIResponse).user
