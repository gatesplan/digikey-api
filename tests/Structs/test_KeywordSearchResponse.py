from ff_digikey_api.Structs.KeywordSearchResponse import KeywordSearchResponse
from ff_digikey_api.Structs.ProductPricingResponse import ProductPricingResponse


SAMPLE_RESPONSE = {
    "Products": [
        {
            "Description": {
                "ProductDescription": "IC MCU 32BIT 512KB FLASH 100LQFP",
                "DetailedDescription": "ARM Cortex-M4 STM32F4",
            },
            "Manufacturer": {"Id": 497, "Name": "STMicroelectronics"},
            "ManufacturerProductNumber": "STM32F407VET6TR",
            "UnitPrice": 10.49,
            "ProductUrl": "https://www.digikey.com/...",
            "ProductVariations": [
                {
                    "DigiKeyProductNumber": "497-19657-1-ND",
                    "PackageType": {"Id": 2, "Name": "Cut Tape (CT)"},
                    "StandardPricing": [
                        {"BreakQuantity": 1, "UnitPrice": 10.49, "TotalPrice": 10.49},
                    ],
                    "QuantityAvailableforPackageType": 3648,
                    "MinimumOrderQuantity": 1,
                    "StandardPackage": 0,
                }
            ],
        }
    ],
    "ProductsCount": 2,
    "ExactMatches": [],
    "FilterOptions": {"ManufacturerFilter": []},
}


class TestKeywordSearchResponse:
    def test_from_dict(self):
        resp = KeywordSearchResponse.from_dict(SAMPLE_RESPONSE)
        assert resp.products_count == 2
        assert len(resp.products) == 1
        assert resp.products[0].manufacturer_product_number == "STM32F407VET6TR"

    def test_from_dict_exact_matches(self):
        resp = KeywordSearchResponse.from_dict(SAMPLE_RESPONSE)
        assert resp.exact_matches == []

    def test_from_dict_filter_options(self):
        resp = KeywordSearchResponse.from_dict(SAMPLE_RESPONSE)
        assert "ManufacturerFilter" in resp.filter_options

    def test_raw_data_preserved(self):
        resp = KeywordSearchResponse.from_dict(SAMPLE_RESPONSE)
        assert resp.raw_data == SAMPLE_RESPONSE

    def test_from_dict_empty(self):
        resp = KeywordSearchResponse.from_dict({})
        assert resp.products == []
        assert resp.products_count == 0


class TestProductPricingResponse:
    def test_from_dict(self):
        data = {
            "Products": SAMPLE_RESPONSE["Products"],
            "ProductsCount": 1,
        }
        resp = ProductPricingResponse.from_dict(data)
        assert resp.products_count == 1
        assert len(resp.products) == 1
        assert resp.products[0].unit_price == 10.49

    def test_from_dict_empty(self):
        resp = ProductPricingResponse.from_dict({})
        assert resp.products == []
        assert resp.products_count == 0
