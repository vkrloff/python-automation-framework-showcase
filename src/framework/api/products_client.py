"""Product catalogue endpoints."""

from framework.api.base_client import BaseApiClient
from framework.models import Product, ProductListResponse


class ProductsClient(BaseApiClient):
    PRODUCTS_PATH = "/api/Products"
    SEARCH_PATH = "/rest/products/search"

    def list_products(self) -> list[Product]:
        return self.parse(self.request("GET", self.PRODUCTS_PATH), ProductListResponse).data

    def search(self, query: str) -> list[Product]:
        response = self.request("GET", self.SEARCH_PATH, params={"q": query})
        return self.parse(response, ProductListResponse).data
