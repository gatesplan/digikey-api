import httpx
import respx
import pytest

from ff_digikey_api.Constants.Endpoints import (
    BASE_URL, KEYWORD_SEARCH, PRODUCT_DETAILS, PRICING,
    MANUFACTURERS, CATEGORIES, CATEGORY_BY_ID,
    ASSOCIATIONS, SUBSTITUTIONS, RECOMMENDED, ALT_PACKAGING,
    MEDIA, DIGIREEL_PRICING, PRICING_OPTIONS,
)
from ff_digikey_api.Core.HttpClient.HttpClient import HttpClient
from ff_digikey_api.Structs.DigiKeyLocale import DigiKeyLocale
from ff_digikey_api.Structs.KeywordSearchRequest import KeywordSearchRequest
from ff_digikey_api.Structs.KeywordSearchResponse import KeywordSearchResponse
from ff_digikey_api.Structs.Product import Product
from ff_digikey_api.Structs.ProductPricingResponse import ProductPricingResponse
from ff_digikey_api.Structs.Manufacturer import Manufacturer
from ff_digikey_api.Structs.Category import Category
from ff_digikey_api.Service.ProductService.ProductService import ProductService


TOKEN = "test-token"

# 최소 Product API 응답 샘플
SAMPLE_PRODUCT = {
    "ManufacturerProductNumber": "STM32F407",
    "Description": {"ProductDescription": "MCU", "DetailedDescription": "ARM MCU"},
    "Manufacturer": {"Id": 1, "Name": "ST"},
    "UnitPrice": 10.0,
    "ProductUrl": "https://digikey.com/test",
}


def _make_service():
    locale = DigiKeyLocale()
    http_client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
    return ProductService(http_client), http_client


class TestProductServiceInit:
    def test_stores_http_client(self):
        svc, client = _make_service()
        assert svc._http_client is client
        client.close()


class TestKeywordSearch:
    @respx.mock
    def test_keyword_search_returns_response(self):
        svc, client = _make_service()
        respx.post(f"{BASE_URL}{KEYWORD_SEARCH}").mock(
            return_value=httpx.Response(200, json={
                "Products": [SAMPLE_PRODUCT],
                "ProductsCount": 1,
            })
        )
        request = KeywordSearchRequest(keywords="STM32")
        result = svc.keyword_search(TOKEN, request)
        assert isinstance(result, KeywordSearchResponse)
        assert result.products_count == 1
        assert result.products[0].manufacturer_product_number == "STM32F407"
        client.close()

    @respx.mock
    def test_keyword_search_sends_post(self):
        svc, client = _make_service()
        route = respx.post(f"{BASE_URL}{KEYWORD_SEARCH}").mock(
            return_value=httpx.Response(200, json={"Products": [], "ProductsCount": 0})
        )
        request = KeywordSearchRequest(keywords="cap", limit=10)
        svc.keyword_search(TOKEN, request)
        assert route.called
        client.close()


class TestProductDetails:
    @respx.mock
    def test_product_details_returns_product(self):
        svc, client = _make_service()
        path = PRODUCT_DETAILS.format(product_number="STM32F407")
        respx.get(f"{BASE_URL}{path}").mock(
            return_value=httpx.Response(200, json={"Product": SAMPLE_PRODUCT})
        )
        result = svc.product_details(TOKEN, "STM32F407")
        assert isinstance(result, Product)
        assert result.manufacturer_product_number == "STM32F407"
        client.close()


class TestPricing:
    @respx.mock
    def test_pricing_returns_response(self):
        svc, client = _make_service()
        path = PRICING.format(product_number="STM32F407")
        respx.get(f"{BASE_URL}{path}").mock(
            return_value=httpx.Response(200, json={
                "Products": [SAMPLE_PRODUCT],
                "ProductsCount": 1,
            })
        )
        result = svc.pricing(TOKEN, "STM32F407")
        assert isinstance(result, ProductPricingResponse)
        assert result.products_count == 1
        client.close()

    @respx.mock
    def test_pricing_with_kwargs(self):
        svc, client = _make_service()
        path = PRICING.format(product_number="STM32F407")
        route = respx.get(f"{BASE_URL}{path}").mock(
            return_value=httpx.Response(200, json={"Products": [], "ProductsCount": 0})
        )
        svc.pricing(TOKEN, "STM32F407", limit=10, offset=0)
        assert route.called
        client.close()


class TestManufacturers:
    @respx.mock
    def test_manufacturers_returns_list(self):
        svc, client = _make_service()
        respx.get(f"{BASE_URL}{MANUFACTURERS}").mock(
            return_value=httpx.Response(200, json={
                "Manufacturers": [
                    {"Id": 1, "Name": "ST"},
                    {"Id": 2, "Name": "TI"},
                ]
            })
        )
        result = svc.manufacturers(TOKEN)
        assert len(result) == 2
        assert all(isinstance(m, Manufacturer) for m in result)
        assert result[0].name == "ST"
        client.close()


class TestCategories:
    @respx.mock
    def test_categories_returns_list(self):
        svc, client = _make_service()
        respx.get(f"{BASE_URL}{CATEGORIES}").mock(
            return_value=httpx.Response(200, json={
                "Categories": [
                    {"Id": 1, "Name": "Capacitors"},
                    {"Id": 2, "Name": "Resistors"},
                ]
            })
        )
        result = svc.categories(TOKEN)
        assert len(result) == 2
        assert all(isinstance(c, Category) for c in result)
        client.close()

    @respx.mock
    def test_category_by_id(self):
        svc, client = _make_service()
        path = CATEGORY_BY_ID.format(category_id=771)
        respx.get(f"{BASE_URL}{path}").mock(
            return_value=httpx.Response(200, json={"Id": 771, "Name": "MCU"})
        )
        result = svc.category(TOKEN, 771)
        assert isinstance(result, Category)
        assert result.id == 771
        client.close()


class TestAssociations:
    @respx.mock
    def test_associations_returns_product_list(self):
        svc, client = _make_service()
        path = ASSOCIATIONS.format(product_number="STM32F407")
        respx.get(f"{BASE_URL}{path}").mock(
            return_value=httpx.Response(200, json={"Products": [SAMPLE_PRODUCT]})
        )
        result = svc.associations(TOKEN, "STM32F407")
        assert len(result) == 1
        assert isinstance(result[0], Product)
        client.close()


class TestSubstitutions:
    @respx.mock
    def test_substitutions_returns_product_list(self):
        svc, client = _make_service()
        path = SUBSTITUTIONS.format(product_number="STM32F407")
        respx.get(f"{BASE_URL}{path}").mock(
            return_value=httpx.Response(200, json={"Products": [SAMPLE_PRODUCT]})
        )
        result = svc.substitutions(TOKEN, "STM32F407")
        assert len(result) == 1
        client.close()


class TestRecommended:
    @respx.mock
    def test_recommended_returns_product_list(self):
        svc, client = _make_service()
        path = RECOMMENDED.format(product_number="STM32F407")
        respx.get(f"{BASE_URL}{path}").mock(
            return_value=httpx.Response(200, json={"Products": [SAMPLE_PRODUCT]})
        )
        result = svc.recommended_products(TOKEN, "STM32F407")
        assert len(result) == 1
        client.close()


class TestAlternatePackaging:
    @respx.mock
    def test_alternate_packaging_returns_product_list(self):
        svc, client = _make_service()
        path = ALT_PACKAGING.format(product_number="STM32F407")
        respx.get(f"{BASE_URL}{path}").mock(
            return_value=httpx.Response(200, json={"Products": [SAMPLE_PRODUCT]})
        )
        result = svc.alternate_packaging(TOKEN, "STM32F407")
        assert len(result) == 1
        client.close()


class TestMedia:
    @respx.mock
    def test_media_returns_dict(self):
        svc, client = _make_service()
        path = MEDIA.format(product_number="STM32F407")
        respx.get(f"{BASE_URL}{path}").mock(
            return_value=httpx.Response(200, json={"MediaLinks": []})
        )
        result = svc.media(TOKEN, "STM32F407")
        assert isinstance(result, dict)
        assert "MediaLinks" in result
        client.close()


class TestDigireelPricing:
    @respx.mock
    def test_digireel_pricing_returns_dict(self):
        svc, client = _make_service()
        path = DIGIREEL_PRICING.format(product_number="STM32F407")
        respx.get(f"{BASE_URL}{path}").mock(
            return_value=httpx.Response(200, json={"UnitPrice": 11.0})
        )
        result = svc.digireel_pricing(TOKEN, "STM32F407")
        assert isinstance(result, dict)
        client.close()


class TestPricingOptions:
    @respx.mock
    def test_pricing_options_returns_dict(self):
        svc, client = _make_service()
        path = PRICING_OPTIONS.format(product_number="STM32F407")
        respx.get(f"{BASE_URL}{path}").mock(
            return_value=httpx.Response(200, json={"Options": []})
        )
        result = svc.pricing_options_by_quantity(TOKEN, "STM32F407")
        assert isinstance(result, dict)
        client.close()
