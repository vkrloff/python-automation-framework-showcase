"""Shared pytest fixtures: settings, API clients and per-test users."""

from collections.abc import Iterator

import pytest

from framework.api import AuthClient, ProductsClient
from framework.config import Settings, get_settings
from framework.data import RegisteredAccount, UserFactory


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Immutable settings, safe to share across the whole session."""
    return get_settings()


@pytest.fixture
def auth_client(settings: Settings) -> Iterator[AuthClient]:
    """Anonymous auth client with its own HTTP session."""
    with AuthClient(settings) as client:
        yield client


@pytest.fixture
def products_client(settings: Settings) -> Iterator[ProductsClient]:
    with ProductsClient(settings) as client:
        yield client


@pytest.fixture
def registered_user(auth_client: AuthClient) -> RegisteredAccount:
    """A fresh user, registered through the API, for every test."""
    credentials = UserFactory.build()
    user = auth_client.register(credentials.to_register_request())
    return RegisteredAccount(id=user.id, credentials=credentials)


@pytest.fixture
def authenticated_client(
    settings: Settings, registered_user: RegisteredAccount
) -> Iterator[AuthClient]:
    """A separate client logged in as `registered_user` (token never leaks to `auth_client`)."""
    with AuthClient(settings) as client:
        authentication = client.login(registered_user.credentials.to_login_request())
        client.set_auth_token(authentication.token)
        yield client
