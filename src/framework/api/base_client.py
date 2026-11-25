"""Base HTTP client: base URL, timeouts, model (de)serialisation and Allure reporting."""

from collections.abc import Mapping
from types import TracebackType
from typing import Self

import allure
import requests
from pydantic import BaseModel

from framework.api.allure_attach import attach_request, attach_response
from framework.config import Settings

JSON_CONTENT_TYPE = "application/json"


def join_url(base: str, path: str) -> str:
    """Join base URL and path with exactly one slash between them."""
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


class BaseApiClient:
    """Thin wrapper over `requests.Session`. Returns data; never asserts expected results."""

    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.api_base_url
        self._timeout = (settings.connect_timeout, settings.read_timeout)
        self._session = requests.Session()
        self._session.headers["Accept"] = JSON_CONTENT_TYPE

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        self._session.close()

    def set_auth_token(self, token: str) -> None:
        """Authenticate the session the way the Juice Shop frontend does.

        Most endpoints read the `Authorization: Bearer` header; some (e.g. `/rest/user/whoami`)
        read the `token` cookie, so both are set.
        """
        self._session.headers["Authorization"] = f"Bearer {token}"
        self._session.cookies.set("token", token)

    def request(
        self,
        method: str,
        path: str,
        *,
        body: BaseModel | None = None,
        params: Mapping[str, str] | None = None,
    ) -> requests.Response:
        """Send a request whose body (if any) is a Pydantic model, serialised by alias."""
        if body is None:
            return self._send(method, path, data=None, content_type=None, params=params)
        data = body.model_dump_json(by_alias=True, exclude_none=True)
        return self._send(method, path, data=data, content_type=JSON_CONTENT_TYPE, params=params)

    def request_raw_body(
        self,
        method: str,
        path: str,
        *,
        raw_body: str | bytes,
        content_type: str = JSON_CONTENT_TYPE,
        params: Mapping[str, str] | None = None,
    ) -> requests.Response:
        """Send `raw_body` exactly as given, bypassing model validation on purpose.

        Intended for negative tests only: malformed JSON, wrong types, missing fields.
        """
        return self._send(method, path, data=raw_body, content_type=content_type, params=params)

    @staticmethod
    def parse[M: BaseModel](response: requests.Response, model: type[M]) -> M:
        """Parse a successful response into `model`; raise `HTTPError` on a non-2xx status.

        This is a precondition for the typed happy-path methods, not a test assertion.
        """
        response.raise_for_status()
        return model.model_validate_json(response.content)

    def _send(
        self,
        method: str,
        path: str,
        *,
        data: str | bytes | None,
        content_type: str | None,
        params: Mapping[str, str] | None,
    ) -> requests.Response:
        headers = {"Content-Type": content_type} if content_type else {}
        url = join_url(self._base_url, path)
        prepared = self._session.prepare_request(
            requests.Request(method, url, headers=headers, data=data, params=params)
        )
        env = self._session.merge_environment_settings(prepared.url, {}, None, None, None)
        with allure.step(f"{method} {path}"):
            attach_request(prepared)
            response = self._session.send(prepared, timeout=self._timeout, **env)
            attach_response(response)
        return response
