"""Base classes and shared types for API models."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, PlainSerializer, SecretStr
from pydantic.alias_generators import to_camel


def _reveal(secret: SecretStr) -> str:
    return secret.get_secret_value()


WireSecret = Annotated[SecretStr, PlainSerializer(_reveal, return_type=str, when_used="json")]
"""A secret that is masked in `repr`/logs and revealed only when serialised to JSON."""


class ApiModel(BaseModel):
    """Base for response models: snake_case in Python, camelCase on the wire.

    Unknown fields are ignored on purpose: we model only the fields the framework uses.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
        extra="ignore",
        frozen=True,
    )


class ApiRequest(ApiModel):
    """Base for request payloads: unknown fields are rejected so typos fail fast."""

    model_config = ConfigDict(extra="forbid")
