import json
from unittest.mock import patch, MagicMock

import pytest

from ff_digikey_api.Structs.KeywordSearchResponse import KeywordSearchResponse
from ff_digikey_api.Structs.Product import Product
from ff_digikey_api.Structs.Manufacturer import Manufacturer
from ff_digikey_api.Structs.Category import Category
from ff_digikey_api.Structs.ProductPricingResponse import ProductPricingResponse


def _make_product(**overrides):
    defaults = dict(
        manufacturer_product_number="TEST-001",
        manufacturer=Manufacturer(id=1, name="TestMfr", raw_data={}),
        description="Test part",
        detailed_description="Test part detailed",
        unit_price=10.5,
        product_url="https://digikey.com/test",
        product_status="Active",
    )
    defaults.update(overrides)
    return Product(**defaults)


MOCK_SEARCH_RESPONSE = KeywordSearchResponse(
    products=[_make_product()],
    products_count=1,
)

MOCK_DETAIL_PRODUCT = _make_product(
    manufacturer_product_number="STM32F407",
    description="IC MCU 32BIT",
    detailed_description="ARM Cortex-M4 MCU",
)

MOCK_PRICING_RESPONSE = ProductPricingResponse(
    products=[_make_product(manufacturer_product_number="STM32F407")],
    products_count=1,
)


@pytest.fixture(autouse=True)
def reset_client():
    """Reset the global _client before each test."""
    import ff_digikey_api.mcp_wrapper.mcp_wrapper as mod
    mod._client = None
    yield
    mod._client = None


@pytest.fixture
def mock_client():
    with patch("ff_digikey_api.mcp_wrapper.mcp_wrapper.DigiKeyClient") as MockCls:
        client = MagicMock()
        client.is_authenticated.return_value = True
        MockCls.from_env.return_value = client
        yield client


class TestDigikeyUsage:
    def test_returns_guide_text(self):
        from ff_digikey_api.mcp_wrapper.mcp_wrapper import digikey_usage

        result = digikey_usage()
        assert "digikey_params" in result
        assert "digikey_parametric_search" in result
        assert "Expression Syntax" in result


class TestDigikeySearch:
    def test_returns_json_with_products(self, mock_client):
        from ff_digikey_api.mcp_wrapper.mcp_wrapper import digikey_search

        mock_client.search.return_value = MOCK_SEARCH_RESPONSE
        result = digikey_search("STM32", limit=5, offset=0)
        data = json.loads(result)
        assert data["products_count"] == 1
        assert data["products"][0]["mpn"] == "TEST-001"
        assert data["products"][0]["manufacturer"] == "TestMfr"
        mock_client.search.assert_called_once_with("STM32", limit=5, offset=0)

    def test_default_params(self, mock_client):
        from ff_digikey_api.mcp_wrapper.mcp_wrapper import digikey_search

        mock_client.search.return_value = MOCK_SEARCH_RESPONSE
        digikey_search("LED")
        mock_client.search.assert_called_once_with("LED", limit=10, offset=0)


class TestDigikeyParametricSearch:
    def test_splits_expressions_and_calls(self, mock_client):
        from ff_digikey_api.mcp_wrapper.mcp_wrapper import digikey_parametric_search

        mock_client.parametric_search.return_value = MOCK_SEARCH_RESPONSE
        result = digikey_parametric_search("resistor", "Resistance>15ohm,Tolerance<=1%")
        data = json.loads(result)
        assert data["products_count"] == 1
        mock_client.parametric_search.assert_called_once_with(
            "resistor",
            expressions=["Resistance>15ohm", "Tolerance<=1%"],
            limit=10,
            offset=0,
            category_id=None,
        )

    def test_single_expression(self, mock_client):
        from ff_digikey_api.mcp_wrapper.mcp_wrapper import digikey_parametric_search

        mock_client.parametric_search.return_value = MOCK_SEARCH_RESPONSE
        digikey_parametric_search("resistor", "Resistance>15ohm")
        mock_client.parametric_search.assert_called_once()
        call_kwargs = mock_client.parametric_search.call_args
        assert call_kwargs[1]["expressions"] == ["Resistance>15ohm"]

    def test_with_category_id(self, mock_client):
        from ff_digikey_api.mcp_wrapper.mcp_wrapper import digikey_parametric_search

        mock_client.parametric_search.return_value = MOCK_SEARCH_RESPONSE
        digikey_parametric_search("resistor", "Resistance>15ohm", category_id=52)
        call_kwargs = mock_client.parametric_search.call_args
        assert call_kwargs[1]["category_id"] == 52

    def test_category_id_zero_means_auto(self, mock_client):
        from ff_digikey_api.mcp_wrapper.mcp_wrapper import digikey_parametric_search

        mock_client.parametric_search.return_value = MOCK_SEARCH_RESPONSE
        digikey_parametric_search("resistor", "Resistance>15ohm", category_id=0)
        call_kwargs = mock_client.parametric_search.call_args
        assert call_kwargs[1]["category_id"] is None


class TestDigikeyParams:
    def test_returns_params_with_explicit_category(self, mock_client):
        from ff_digikey_api.mcp_wrapper.mcp_wrapper import digikey_params

        mock_client.search.return_value = KeywordSearchResponse(
            products=[], products_count=0,
            filter_options={
                "ParametricFilters": [
                    {
                        "ParameterId": 2085,
                        "ParameterName": "Resistance",
                        "FilterValues": [
                            {"ValueId": "100", "ValueName": "10 Ohms"},
                            {"ValueId": "101", "ValueName": "22 Ohms"},
                        ],
                    },
                ],
            },
        )
        result = digikey_params("resistor", category_id=52)
        data = json.loads(result)
        assert data["category_id"] == 52
        assert len(data["parameters"]) == 1
        assert data["parameters"][0]["name"] == "Resistance"
        assert data["parameters"][0]["values_count"] == 2

    def test_auto_detects_category(self, mock_client):
        from ff_digikey_api.mcp_wrapper.mcp_wrapper import digikey_params

        mock_client.detect_leaf_category.return_value = 52
        mock_client.search.return_value = KeywordSearchResponse(
            products=[], products_count=0,
            filter_options={
                "ParametricFilters": [
                    {"ParameterId": 1, "ParameterName": "P", "FilterValues": []},
                ],
            },
        )
        result = digikey_params("resistor")
        data = json.loads(result)
        assert data["category_id"] == 52
        mock_client.detect_leaf_category.assert_called_once_with("resistor")


class TestDigikeyDetails:
    def test_returns_product_json(self, mock_client):
        from ff_digikey_api.mcp_wrapper.mcp_wrapper import digikey_details

        mock_client.product_details.return_value = MOCK_DETAIL_PRODUCT
        result = digikey_details("STM32F407")
        data = json.loads(result)
        assert data["mpn"] == "STM32F407"
        assert data["description"] == "IC MCU 32BIT"
        mock_client.product_details.assert_called_once_with("STM32F407")


class TestDigikeyPricing:
    def test_returns_pricing_json(self, mock_client):
        from ff_digikey_api.mcp_wrapper.mcp_wrapper import digikey_pricing

        mock_client.pricing.return_value = MOCK_PRICING_RESPONSE
        result = digikey_pricing("STM32F407")
        data = json.loads(result)
        assert data["products_count"] == 1
        assert data["products"][0]["mpn"] == "STM32F407"
        mock_client.pricing.assert_called_once_with("STM32F407")


class TestGetClient:
    def test_lazy_init(self, mock_client):
        from ff_digikey_api.mcp_wrapper.mcp_wrapper import _get_client, DigiKeyClient

        c1 = _get_client()
        c2 = _get_client()
        assert c1 is c2
        DigiKeyClient.from_env.assert_called_once()

    def test_auto_authorize_if_not_authenticated(self):
        with patch("ff_digikey_api.mcp_wrapper.mcp_wrapper.DigiKeyClient") as MockCls:
            client = MagicMock()
            client.is_authenticated.return_value = False
            MockCls.from_env.return_value = client

            from ff_digikey_api.mcp_wrapper.mcp_wrapper import _get_client
            _get_client()
            client.authorize.assert_called_once()

    def test_error_returns_json_error(self, mock_client):
        from ff_digikey_api.mcp_wrapper.mcp_wrapper import digikey_search

        mock_client.search.side_effect = Exception("API failed")
        result = digikey_search("test")
        data = json.loads(result)
        assert "error" in data
        assert "API failed" in data["message"]
