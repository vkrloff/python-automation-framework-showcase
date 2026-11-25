"""Product models (`/api/Products`, `/rest/products/search`).

Timestamps are deliberately not modelled: the two endpoints return them in different formats.
"""

from typing import Literal

from framework.models.base import ApiModel


class Product(ApiModel):
    id: int
    name: str
    description: str
    price: float
    deluxe_price: float
    image: str


class ProductListResponse(ApiModel):
    status: Literal["success"]
    data: list[Product]
