import argparse
import json
import sys

from loguru import logger

from ff_digikey_api.Constants.Endpoints import DEFAULT_SEARCH_LIMIT


def _suppress_loguru():
    logger.remove()


def _make_client():
    from ff_digikey_api import DigiKeyClient
    return DigiKeyClient.from_env(".env")


def _auto_authorize(client):
    if not client.is_authenticated():
        client.authorize()


def _cmd_authorize(args):
    client = _make_client()
    try:
        client.authorize()
        print(json.dumps({"status": "ok", "message": "Authorization successful"}))
    finally:
        client.close()


def _cmd_search(args):
    client = _make_client()
    try:
        _auto_authorize(client)
        if args.params:
            result = client.parametric_search(
                args.keywords, expressions=args.params,
                limit=args.limit, offset=args.offset,
            )
        else:
            result = client.search(args.keywords, limit=args.limit, offset=args.offset)
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
        print(json.dumps(output, indent=2))
    finally:
        client.close()


def _cmd_details(args):
    client = _make_client()
    try:
        _auto_authorize(client)
        p = client.product_details(args.product_number)
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
        print(json.dumps(output, indent=2))
    finally:
        client.close()


def _cmd_params(args):
    from ff_digikey_api import DigiKeyClient, FilterOptions

    client = _make_client()
    try:
        _auto_authorize(client)
        cat_id = args.category
        if cat_id is None:
            cat_id = client.detect_leaf_category(args.keywords or "")
            if cat_id is None:
                raise ValueError("category not found from search results")

        result = client.search(args.keywords or "", limit=1, filters=FilterOptions(category_ids=[cat_id]))
        pf = result.filter_options.get("ParametricFilters")
        if not pf:
            raise ValueError("ParametricFilters not found (category_id={})".format(cat_id))

        output = {
            "category_id": cat_id,
            "parameters": [
                {
                    "id": p["ParameterId"],
                    "name": p["ParameterName"],
                    "values_count": len(p.get("FilterValues", [])),
                    "values": [
                        {"id": v["ValueId"], "name": v["ValueName"]}
                        for v in p.get("FilterValues", [])[:20]
                    ],
                }
                for p in pf
            ],
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    finally:
        client.close()


def _cmd_pricing(args):
    client = _make_client()
    try:
        _auto_authorize(client)
        result = client.pricing(args.product_number)
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
        print(json.dumps(output, indent=2))
    finally:
        client.close()


def main():
    _suppress_loguru()

    parser = argparse.ArgumentParser(
        prog="ff-digikey",
        description="DigiKey Product Information V4 API CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # authorize
    subparsers.add_parser("authorize", help="OAuth 2.0 authorization")

    # search
    sp_search = subparsers.add_parser("search", help="Keyword search")
    sp_search.add_argument("keywords", help="Search keywords")
    sp_search.add_argument("--limit", type=int, default=DEFAULT_SEARCH_LIMIT,
                           help=f"Max results (default: {DEFAULT_SEARCH_LIMIT}, max 50)")
    sp_search.add_argument("--offset", type=int, default=0, help="Result offset")
    sp_search.add_argument("-p", "--param", dest="params", action="append", default=[],
                           help="Parametric filter (e.g. 'Resistance>15ohm')")

    # params
    sp_params = subparsers.add_parser("params", help="List parametric filter options")
    sp_params.add_argument("keywords", nargs="?", default=None, help="Search keywords (for auto category detection)")
    sp_params.add_argument("--category", type=int, default=None, help="Category ID (skip auto detection)")

    # details
    sp_details = subparsers.add_parser("details", help="Product details by MPN")
    sp_details.add_argument("product_number", help="Manufacturer part number")

    # pricing
    sp_pricing = subparsers.add_parser("pricing", help="Product pricing by MPN")
    sp_pricing.add_argument("product_number", help="Manufacturer part number")

    args = parser.parse_args()

    try:
        handlers = {
            "authorize": _cmd_authorize,
            "search": _cmd_search,
            "params": _cmd_params,
            "details": _cmd_details,
            "pricing": _cmd_pricing,
        }
        handlers[args.command](args)
    except Exception as e:
        print(json.dumps({"error": type(e).__name__, "message": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
