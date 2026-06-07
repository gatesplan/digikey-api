from loguru import logger

from ff_digikey_api.Constants.Endpoints import (
    KEYWORD_SEARCH, PRODUCT_DETAILS, PRICING, PRICING_OPTIONS,
    MEDIA, ASSOCIATIONS, SUBSTITUTIONS, RECOMMENDED,
    ALT_PACKAGING, DIGIREEL_PRICING,
    MANUFACTURERS, CATEGORIES, CATEGORY_BY_ID,
)
from ff_digikey_api.Core.HttpClient.HttpClient import HttpClient
from ff_digikey_api.Structs.KeywordSearchRequest import KeywordSearchRequest
from ff_digikey_api.Structs.KeywordSearchResponse import KeywordSearchResponse
from ff_digikey_api.Structs.Product import Product
from ff_digikey_api.Structs.ProductPricingResponse import ProductPricingResponse
from ff_digikey_api.Structs.Manufacturer import Manufacturer
from ff_digikey_api.Structs.Category import Category


class ProductService:
    def __init__(self, http_client: HttpClient):
        self._http_client = http_client
        logger.info("ProductService 초기화")

    # --- 검색 ---

    def keyword_search(self, token: str, request: KeywordSearchRequest) -> KeywordSearchResponse:
        logger.info("keyword_search 시작")
        data = self._http_client.post(KEYWORD_SEARCH, token, request.to_dict())
        return KeywordSearchResponse.from_dict(data)

    def product_details(self, token: str, product_number: str) -> Product:
        logger.info(f"product_details 시작: product_number={product_number}")
        path = PRODUCT_DETAILS.format(product_number=product_number)
        data = self._http_client.get(path, token)
        return Product.from_dict(data.get("Product", data))

    def pricing(self, token: str, product_number: str, **kwargs) -> ProductPricingResponse:
        logger.info(f"pricing 시작: product_number={product_number}")
        path = PRICING.format(product_number=product_number)
        params = kwargs if kwargs else None
        data = self._http_client.get(path, token, params=params)
        return ProductPricingResponse.from_dict(data)

    # --- 연관/대체 ---

    def associations(self, token: str, product_number: str) -> list[Product]:
        logger.info(f"associations 시작: product_number={product_number}")
        return self._get_product_list(token, ASSOCIATIONS, product_number)

    def substitutions(self, token: str, product_number: str) -> list[Product]:
        logger.info(f"substitutions 시작: product_number={product_number}")
        return self._get_product_list(token, SUBSTITUTIONS, product_number)

    def recommended_products(self, token: str, product_number: str) -> list[Product]:
        logger.info(f"recommended_products 시작: product_number={product_number}")
        return self._get_product_list(token, RECOMMENDED, product_number)

    def alternate_packaging(self, token: str, product_number: str) -> list[Product]:
        logger.info(f"alternate_packaging 시작: product_number={product_number}")
        return self._get_product_list(token, ALT_PACKAGING, product_number)

    # --- 기타 ---

    def media(self, token: str, product_number: str) -> dict:
        logger.info(f"media 시작: product_number={product_number}")
        path = MEDIA.format(product_number=product_number)
        return self._http_client.get(path, token)

    def digireel_pricing(self, token: str, product_number: str, requested_quantity: int = 1) -> dict:
        logger.info(f"digireel_pricing 시작: product_number={product_number}")
        path = DIGIREEL_PRICING.format(product_number=product_number)
        params = {"requestedQuantity": requested_quantity}
        return self._http_client.get(path, token, params=params)

    def pricing_options_by_quantity(self, token: str, product_number: str) -> dict:
        logger.info(f"pricing_options_by_quantity 시작: product_number={product_number}")
        path = PRICING_OPTIONS.format(product_number=product_number)
        return self._http_client.get(path, token)

    # --- 참조 데이터 ---

    def manufacturers(self, token: str) -> list[Manufacturer]:
        logger.info("manufacturers 시작")
        data = self._http_client.get(MANUFACTURERS, token)
        return [Manufacturer.from_dict(m) for m in data.get("Manufacturers", [])]

    def categories(self, token: str) -> list[Category]:
        logger.info("categories 시작")
        data = self._http_client.get(CATEGORIES, token)
        return [Category.from_dict(c) for c in data.get("Categories", [])]

    def category(self, token: str, category_id: int) -> Category:
        logger.info(f"category 시작: category_id={category_id}")
        path = CATEGORY_BY_ID.format(category_id=category_id)
        data = self._http_client.get(path, token)
        return Category.from_dict(data)

    # --- 내부 헬퍼 ---

    def _get_product_list(self, token: str, endpoint: str, product_number: str) -> list[Product]:
        path = endpoint.format(product_number=product_number)
        data = self._http_client.get(path, token)
        return [Product.from_dict(p) for p in data.get("Products", [])]
