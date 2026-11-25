"""Allure attachments for HTTP exchanges, with secrets masked."""

import json
import shlex
from collections.abc import Mapping

import allure
from pydantic import JsonValue
from requests import PreparedRequest, Response

MASK = "***"
SENSITIVE_HEADERS = frozenset({"authorization", "cookie", "set-cookie"})
SENSITIVE_BODY_KEYS = frozenset({"password", "passwordRepeat", "token"})
_CURL_SKIPPED_HEADERS = frozenset({"content-length"})


def mask_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {k: MASK if k.lower() in SENSITIVE_HEADERS else v for k, v in headers.items()}


def mask_body(body: str | bytes | None, *, indent: int | None = 2) -> str:
    """Mask sensitive JSON keys; non-JSON bodies are returned unchanged."""
    if body is None:
        return ""
    text = body.decode("utf-8", errors="replace") if isinstance(body, bytes) else body
    try:
        parsed: JsonValue = json.loads(text)
    except ValueError:
        return text
    return json.dumps(_mask_json(parsed), indent=indent, ensure_ascii=False)


def _mask_json(value: JsonValue) -> JsonValue:
    if isinstance(value, dict):
        return {k: MASK if k in SENSITIVE_BODY_KEYS else _mask_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_mask_json(item) for item in value]
    return value


def to_curl(request: PreparedRequest) -> str:
    """Build a copy-pasteable curl command equivalent to `request` (secrets masked)."""
    parts = ["curl", "-X", request.method or "GET", shlex.quote(request.url or "")]
    for name, value in mask_headers(request.headers).items():
        if name.lower() not in _CURL_SKIPPED_HEADERS:
            parts += ["-H", shlex.quote(f"{name}: {value}")]
    if request.body:
        parts += ["--data-raw", shlex.quote(mask_body(request.body, indent=None))]
    return " ".join(parts)


def _format_headers(headers: Mapping[str, str]) -> str:
    return "\n".join(f"{k}: {v}" for k, v in mask_headers(headers).items())


def attach_request(request: PreparedRequest) -> None:
    text = (
        f"{request.method} {request.url}\n"
        f"{_format_headers(request.headers)}\n\n"
        f"{mask_body(request.body)}"
    )
    allure.attach(text, name="request", attachment_type=allure.attachment_type.TEXT)
    allure.attach(to_curl(request), name="curl", attachment_type=allure.attachment_type.TEXT)


def attach_response(response: Response) -> None:
    text = (
        f"{response.status_code} {response.reason}\n"
        f"{_format_headers(response.headers)}\n\n"
        f"{mask_body(response.content)}"
    )
    allure.attach(
        text,
        name=f"response {response.status_code}",
        attachment_type=allure.attachment_type.TEXT,
    )
