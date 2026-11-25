"""Registration and login."""

from http import HTTPStatus

import pytest

from framework.api import AuthClient
from framework.data import RegisteredAccount, UserFactory
from framework.models import RegisterResponse

pytestmark = pytest.mark.api

JWT_PARTS = 3


@pytest.mark.smoke
def test_register_new_user(auth_client: AuthClient) -> None:
    credentials = UserFactory.build()

    response = auth_client.register_raw(credentials.to_register_request())

    assert response.status_code == HTTPStatus.CREATED
    user = RegisterResponse.model_validate_json(response.content).data
    assert user.email == credentials.email
    assert user.role == "customer"
    assert user.id > 0


@pytest.mark.smoke
def test_login_returns_token(auth_client: AuthClient, registered_user: RegisteredAccount) -> None:
    authentication = auth_client.login(registered_user.credentials.to_login_request())

    assert authentication.umail == registered_user.credentials.email
    assert len(authentication.token.split(".")) == JWT_PARTS
    assert all(authentication.token.split("."))


def test_login_with_wrong_password_is_rejected(
    auth_client: AuthClient, registered_user: RegisteredAccount
) -> None:
    wrong_password = UserFactory.build(email=registered_user.credentials.email)

    response = auth_client.login_raw(wrong_password.to_login_request())

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert "authentication" not in response.text


def test_authenticated_client_is_recognised(
    authenticated_client: AuthClient, registered_user: RegisteredAccount
) -> None:
    me = authenticated_client.whoami()

    assert me is not None, "token was not accepted: whoami returned an anonymous user"
    assert me.id == registered_user.id
    assert me.email == registered_user.credentials.email
