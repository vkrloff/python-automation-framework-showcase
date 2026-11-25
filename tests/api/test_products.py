"""Product catalogue and search."""

from uuid import uuid4

import pytest

from framework.api import ProductsClient

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_product_list_matches_model(products_client: ProductsClient) -> None:
    products = products_client.list_products()  # parsing validates every item against `Product`

    assert products, "product catalogue is empty"
    ids = [product.id for product in products]
    assert len(ids) == len(set(ids)), "product ids are not unique"
    assert all(product.price > 0 for product in products)


@pytest.mark.parametrize("term", ["apple", "juice"])
def test_search_returns_matching_products(products_client: ProductsClient, term: str) -> None:
    results = products_client.search(term)

    assert results, f"no products found for {term!r}"
    # Juice Shop searches name OR description, case-insensitively.
    mismatches = [
        p.name for p in results if term not in p.name.lower() and term not in p.description.lower()
    ]
    assert not mismatches, f"products not matching {term!r}: {mismatches}"


def test_search_without_matches_returns_empty_list(products_client: ProductsClient) -> None:
    assert products_client.search(f"no-match-{uuid4().hex}") == []
