import json

from loguru import logger
from mcp.server.fastmcp import FastMCP

from ..API.DigiKeyClient.DigiKeyClient import DigiKeyClient
from ..Structs.FilterOptions import FilterOptions
from ..Constants.Endpoints import DEFAULT_SEARCH_LIMIT

logger.remove()

mcp = FastMCP("digikey", instructions="DigiKey V4 API. Call digikey_usage() first for full usage guide.")

_client = None


def _get_client() -> DigiKeyClient:
    global _client
    if _client is None:
        _client = DigiKeyClient.from_env()
        if not _client.is_authenticated():
            _client.authorize()
    return _client


def _format_search_result(result) -> str:
    output = {
        "products_count": result.products_count,
        "products": [
            {
                "mpn": p.manufacturer_product_number,
                "manufacturer": p.manufacturer.name,
                "description": p.description,
                "unit_price": p.unit_price,
                "product_url": p.product_url,
                "status": p.product_status,
            }
            for p in result.products
        ],
    }
    return json.dumps(output, indent=2)


def _format_detail(p) -> str:
    output = {
        "mpn": p.manufacturer_product_number,
        "manufacturer": p.manufacturer.name,
        "description": p.description,
        "detailed_description": p.detailed_description,
        "unit_price": p.unit_price,
        "status": p.product_status,
        "product_url": p.product_url,
        "datasheet_url": p.datasheet_url,
        "category": p.category.name if p.category else None,
        "parameters": [
            {"name": param.name, "value": param.value}
            for param in p.parameters
        ],
        "variations": [
            {
                "digi_key_pn": v.digi_key_product_number,
                "package_type": v.package_type,
                "quantity_available": v.quantity_available,
                "min_order_quantity": v.min_order_quantity,
                "pricing": [
                    {"qty": pb.break_quantity, "unit_price": pb.unit_price}
                    for pb in v.standard_pricing
                ],
            }
            for v in p.product_variations
        ],
    }
    return json.dumps(output, indent=2)


def _format_pricing(result) -> str:
    output = {
        "products_count": result.products_count,
        "products": [
            {
                "mpn": p.manufacturer_product_number,
                "variations": [
                    {
                        "digi_key_pn": v.digi_key_product_number,
                        "package_type": v.package_type,
                        "quantity_available": v.quantity_available,
                        "pricing": [
                            {"qty": pb.break_quantity, "unit_price": pb.unit_price}
                            for pb in v.standard_pricing
                        ],
                    }
                    for v in p.product_variations
                ],
            }
            for p in result.products
        ],
    }
    return json.dumps(output, indent=2)


def _error_json(e: Exception) -> str:
    return json.dumps({"error": type(e).__name__, "message": str(e)})


@mcp.tool()
def digikey_usage() -> str:
    """Returns full usage guide for all DigiKey tools. Call this first."""
    return """# DigiKey MCP Tools Usage Guide

## Workflow

1. digikey_search -- keyword search (simple)
2. digikey_params -- discover filter parameter names for a category
3. digikey_parametric_search -- filtered search using parameter expressions
4. digikey_details -- full product info by MPN
5. digikey_pricing -- pricing/stock info by MPN

## Parametric Search Flow (2-step)

Parameter names depend on locale (e.g. Korean locale: "Resistance" -> "저항").
Always call digikey_params first to discover available parameter names.

Step 1: digikey_params("resistor")
  -> returns: category_id, parameter names (Resistance, Tolerance, Power, ...) with sample values

Step 2: digikey_parametric_search("resistor", "Resistance>10kohm,Tolerance<=1%")
  -> returns: filtered products

## Expression Syntax (for digikey_parametric_search)

Operators: =, !=, >, >=, <, <=
SI prefixes: p(pico), n(nano), u(micro), m(milli), k(kilo), M(mega), G(giga)
Examples: "Resistance>10kohm", "Tolerance<=1%", "Color=Green", "Capacitance>=100uF"

Multiple expressions: comma-separated string
  "Resistance>10kohm,Tolerance<=1%"

## Locale

English locale recommended. Parameter names and filter values are most reliable in English.
Set DIGIKEY_LANGUAGE=en in MCP env config. Other locales may have inconsistent translations.

## Error Handling

All tools return JSON. On error: {"error": "ErrorType", "message": "..."}
Auth is client_credentials (2-legged): tokens auto-issue/refresh, no manual step.
TokenExpiredError means invalid DIGIKEY_CLIENT_ID/SECRET -- fix the env config.
"""


@mcp.tool()
def digikey_search(keywords: str, limit: int = DEFAULT_SEARCH_LIMIT, offset: int = 0) -> str:
    """Keyword search. Returns products with mpn, manufacturer, price, status."""
    try:
        client = _get_client()
        result = client.search(keywords, limit=limit, offset=offset)
        return _format_search_result(result)
    except Exception as e:
        return _error_json(e)


@mcp.tool()
def digikey_parametric_search(
    keywords: str,
    expressions: str,
    limit: int = DEFAULT_SEARCH_LIMIT,
    offset: int = 0,
    category_id: int = 0,
) -> str:
    """Filtered search with parameter expressions. Call digikey_params first to get parameter names.
    expressions: comma-separated (e.g. "Resistance>10kohm,Tolerance<=1%"). category_id 0 = auto-detect."""
    try:
        client = _get_client()
        expr_list = [e.strip() for e in expressions.split(",") if e.strip()]
        cat = category_id if category_id != 0 else None
        result = client.parametric_search(
            keywords,
            expressions=expr_list,
            limit=limit,
            offset=offset,
            category_id=cat,
        )
        return _format_search_result(result)
    except Exception as e:
        return _error_json(e)


@mcp.tool()
def digikey_params(keywords: str, category_id: int = 0) -> str:
    """Discover available filter parameter names and sample values for a category. Call before parametric_search."""
    try:
        client = _get_client()
        cat = category_id if category_id != 0 else None

        if cat is None:
            cat = client.detect_leaf_category(keywords)
            if cat is None:
                return _error_json(ValueError("category not found from search results"))

        result = client.search(keywords, limit=1, filters=FilterOptions(category_ids=[cat]))
        pf = result.filter_options.get("ParametricFilters")
        if not pf:
            return _error_json(ValueError("ParametricFilters not found (category_id={})".format(cat)))

        output = {
            "category_id": cat,
            "parameters": [
                {
                    "id": p["ParameterId"],
                    "name": p["ParameterName"],
                    "values_count": len(p.get("FilterValues", [])),
                    "sample_values": [
                        v["ValueName"] for v in p.get("FilterValues", [])[:10]
                    ],
                }
                for p in pf
            ],
        }
        return json.dumps(output, indent=2, ensure_ascii=False)
    except Exception as e:
        return _error_json(e)


@mcp.tool()
def digikey_details(product_number: str) -> str:
    """Full product info by MPN: specs, datasheet, variations, pricing tiers."""
    try:
        client = _get_client()
        p = client.product_details(product_number)
        return _format_detail(p)
    except Exception as e:
        return _error_json(e)


@mcp.tool()
def digikey_pricing(product_number: str) -> str:
    """Pricing and stock info by MPN: variations, quantity breaks, availability."""
    try:
        client = _get_client()
        result = client.pricing(product_number)
        return _format_pricing(result)
    except Exception as e:
        return _error_json(e)
