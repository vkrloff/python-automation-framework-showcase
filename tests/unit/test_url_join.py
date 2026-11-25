"""URL joining never produces a double slash (no SUT needed)."""

import pytest

from framework.api.base_client import join_url


@pytest.mark.parametrize(
    ("base", "path"),
    [
        ("http://host:3000", "api/Products"),
        ("http://host:3000", "/api/Products"),
        ("http://host:3000/", "api/Products"),
        ("http://host:3000/", "/api/Products"),
    ],
)
def test_join_url_uses_single_slash(base: str, path: str) -> None:
    assert join_url(base, path) == "http://host:3000/api/Products"
