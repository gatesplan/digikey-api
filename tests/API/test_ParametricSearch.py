from unittest.mock import patch, MagicMock

import pytest

from ff_digikey_api.API.DigiKeyClient.DigiKeyClient import DigiKeyClient
from ff_digikey_api.Structs.KeywordSearchResponse import KeywordSearchResponse
from ff_digikey_api.Structs.Product import Product
from ff_digikey_api.Structs.Manufacturer import Manufacturer
from ff_digikey_api.Structs.Category import Category
from ff_digikey_api.Structs.FilterOptions import FilterOptions


def _product_with_category(cat_id):
    return Product(
        manufacturer_product_number="TEST",
        manufacturer=Manufacturer(id=1, name="M", raw_data={}),
        description="d", detailed_description="dd",
        unit_price=1.0, product_url="u",
        category=Category(id=cat_id, name="Cat", children=[], raw_data={}),
    )


PROBE_FILTER_OPTIONS = {
    "ParametricFilters": [
        {
            "ParameterId": 2085,
            "ParameterName": "Resistance",
            "FilterValues": [
                {"ValueId": "100", "ValueName": "10 Ohms", "ProductCount": 500},
                {"ValueId": "101", "ValueName": "15 Ohms", "ProductCount": 300},
                {"ValueId": "102", "ValueName": "22 Ohms", "ProductCount": 200},
                {"ValueId": "103", "ValueName": "1.5 kOhms", "ProductCount": 150},
            ],
        },
        {
            "ParameterId": 3050,
            "ParameterName": "Tolerance",
            "FilterValues": [
                {"ValueId": "200", "ValueName": "0.1%", "ProductCount": 50},
                {"ValueId": "201", "ValueName": "1%", "ProductCount": 400},
                {"ValueId": "202", "ValueName": "5%", "ProductCount": 600},
            ],
        },
    ],
}

# category_id 미지정 시: 1차(카테고리 추출) + 2차(probe) + 3차(필터 적용) = 3회
PRE_RESPONSE = KeywordSearchResponse(
    products=[_product_with_category(52)],
    products_count=100,
)

PROBE_RESPONSE = KeywordSearchResponse(
    products=[], products_count=1500,
    filter_options=PROBE_FILTER_OPTIONS,
)

FILTERED_RESPONSE = KeywordSearchResponse(
    products=[], products_count=42,
)


def _make_client():
    return DigiKeyClient(client_id="cid", client_secret="csec")


class TestParametricSearchWithExplicitCategory:
    """category_id 지정 시: probe + filtered = 2회 호출."""

    def test_calls_search_twice(self):
        client = _make_client()
        with patch.object(client._token_manager, "get_access_token", return_value="t"):
            with patch.object(
                client._product_service, "keyword_search",
                side_effect=[PROBE_RESPONSE, FILTERED_RESPONSE],
            ) as mock_ks:
                client.parametric_search("resistor", ["Resistance>15ohm"], category_id=52)
                assert mock_ks.call_count == 2
        client.close()

    def test_probe_has_category_filter(self):
        client = _make_client()
        with patch.object(client._token_manager, "get_access_token", return_value="t"):
            with patch.object(
                client._product_service, "keyword_search",
                side_effect=[PROBE_RESPONSE, FILTERED_RESPONSE],
            ) as mock_ks:
                client.parametric_search("resistor", ["Resistance>15ohm"], category_id=52)
                probe_req = mock_ks.call_args_list[0][0][1]
                assert 52 in probe_req.filters.category_ids

    def test_probe_uses_limit_1(self):
        client = _make_client()
        with patch.object(client._token_manager, "get_access_token", return_value="t"):
            with patch.object(
                client._product_service, "keyword_search",
                side_effect=[PROBE_RESPONSE, FILTERED_RESPONSE],
            ) as mock_ks:
                client.parametric_search("resistor", ["Resistance>15ohm"], category_id=52)
                probe_req = mock_ks.call_args_list[0][0][1]
                assert probe_req.limit == 1

    def test_filtered_uses_user_limit(self):
        client = _make_client()
        with patch.object(client._token_manager, "get_access_token", return_value="t"):
            with patch.object(
                client._product_service, "keyword_search",
                side_effect=[PROBE_RESPONSE, FILTERED_RESPONSE],
            ) as mock_ks:
                client.parametric_search("resistor", ["Resistance>15ohm"], limit=25, offset=10, category_id=52)
                filtered_req = mock_ks.call_args_list[1][0][1]
                assert filtered_req.limit == 25
                assert filtered_req.offset == 10

    def test_filtered_has_parametric_filter(self):
        client = _make_client()
        with patch.object(client._token_manager, "get_access_token", return_value="t"):
            with patch.object(
                client._product_service, "keyword_search",
                side_effect=[PROBE_RESPONSE, FILTERED_RESPONSE],
            ) as mock_ks:
                client.parametric_search("resistor", ["Resistance>15ohm"], category_id=52)
                filtered_req = mock_ks.call_args_list[1][0][1]
                pf = filtered_req.filters.parametric_filter
                assert pf is not None
                assert pf.parameter_filters[0].parameter_id == 2085
                assert pf.parameter_filters[0].value_ids == ["102", "103"]

    def test_returns_filtered_response(self):
        client = _make_client()
        with patch.object(client._token_manager, "get_access_token", return_value="t"):
            with patch.object(
                client._product_service, "keyword_search",
                side_effect=[PROBE_RESPONSE, FILTERED_RESPONSE],
            ):
                result = client.parametric_search("resistor", ["Resistance>15ohm"], category_id=52)
                assert result.products_count == 42
        client.close()

    def test_single_expression_string(self):
        client = _make_client()
        with patch.object(client._token_manager, "get_access_token", return_value="t"):
            with patch.object(
                client._product_service, "keyword_search",
                side_effect=[PROBE_RESPONSE, FILTERED_RESPONSE],
            ) as mock_ks:
                client.parametric_search("resistor", "Resistance>15ohm", category_id=52)
                assert mock_ks.call_count == 2
        client.close()

    def test_multiple_expressions(self):
        client = _make_client()
        with patch.object(client._token_manager, "get_access_token", return_value="t"):
            with patch.object(
                client._product_service, "keyword_search",
                side_effect=[PROBE_RESPONSE, FILTERED_RESPONSE],
            ) as mock_ks:
                client.parametric_search("resistor", ["Resistance>15ohm", "Tolerance<=1%"], category_id=52)
                filtered_req = mock_ks.call_args_list[1][0][1]
                assert len(filtered_req.filters.parametric_filter.parameter_filters) == 2
        client.close()

    def test_preserves_existing_filters(self):
        client = _make_client()
        user_filters = FilterOptions(manufacturer_ids=[497])
        with patch.object(client._token_manager, "get_access_token", return_value="t"):
            with patch.object(
                client._product_service, "keyword_search",
                side_effect=[PROBE_RESPONSE, FILTERED_RESPONSE],
            ) as mock_ks:
                client.parametric_search("resistor", ["Resistance>15ohm"], filters=user_filters, category_id=52)
                filtered_req = mock_ks.call_args_list[1][0][1]
                assert 497 in filtered_req.filters.manufacturer_ids
        client.close()


class TestParametricSearchAutoCategory:
    """category_id 미지정 시: pre(카테고리 추출) + probe + filtered = 3회."""

    def test_calls_search_three_times(self):
        client = _make_client()
        with patch.object(client._token_manager, "get_access_token", return_value="t"):
            with patch.object(
                client._product_service, "keyword_search",
                side_effect=[PRE_RESPONSE, PROBE_RESPONSE, FILTERED_RESPONSE],
            ) as mock_ks:
                client.parametric_search("resistor", ["Resistance>15ohm"])
                assert mock_ks.call_count == 3
        client.close()

    def test_extracts_category_from_products(self):
        client = _make_client()
        with patch.object(client._token_manager, "get_access_token", return_value="t"):
            with patch.object(
                client._product_service, "keyword_search",
                side_effect=[PRE_RESPONSE, PROBE_RESPONSE, FILTERED_RESPONSE],
            ) as mock_ks:
                client.parametric_search("resistor", ["Resistance>15ohm"])
                # probe (2nd call) should have category 52 from pre-search products
                probe_req = mock_ks.call_args_list[1][0][1]
                assert 52 in probe_req.filters.category_ids

    def test_no_products_with_category_raises(self):
        no_cat_product = Product(
            manufacturer_product_number="X", description="d", detailed_description="dd",
            manufacturer=Manufacturer(id=1, name="M", raw_data={}),
            unit_price=1.0, product_url="u",
        )
        no_cat_response = KeywordSearchResponse(products=[no_cat_product], products_count=1)
        client = _make_client()
        with patch.object(client._token_manager, "get_access_token", return_value="t"):
            with patch.object(
                client._product_service, "keyword_search",
                return_value=no_cat_response,
            ):
                with pytest.raises(ValueError, match="category"):
                    client.parametric_search("xyz", ["Resistance>15ohm"])
        client.close()

    def test_no_parametric_filters_raises(self):
        empty_probe = KeywordSearchResponse(products=[], products_count=0, filter_options={})
        client = _make_client()
        with patch.object(client._token_manager, "get_access_token", return_value="t"):
            with patch.object(
                client._product_service, "keyword_search",
                side_effect=[PRE_RESPONSE, empty_probe],
            ):
                with pytest.raises(ValueError, match="ParametricFilters"):
                    client.parametric_search("resistor", ["Resistance>15ohm"])
        client.close()
