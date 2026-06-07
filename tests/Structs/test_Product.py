from ff_digikey_api.Structs.Product import Product
from ff_digikey_api.Structs.Manufacturer import Manufacturer
from ff_digikey_api.Structs.Category import Category
from ff_digikey_api.Structs.Parameter import Parameter
from ff_digikey_api.Structs.ProductVariation import ProductVariation
from ff_digikey_api.Structs.PriceBreak import PriceBreak


# 실제 DigiKey API 응답 샘플
SAMPLE_PRODUCT_DATA = {
    "Description": {
        "ProductDescription": "IC MCU 32BIT 512KB FLASH 100LQFP",
        "DetailedDescription": "ARM Cortex-M4 STM32F4 Microcontroller IC 32-Bit 168MHz 512KB (512K x 8) FLASH 100-LQFP (14x14)",
    },
    "Manufacturer": {"Id": 497, "Name": "STMicroelectronics"},
    "ManufacturerProductNumber": "STM32F407VET6TR",
    "UnitPrice": 10.49,
    "ProductUrl": "https://www.digikey.com/en/products/detail/stmicroelectronics/STM32F407VET6TR/5268287",
    "DatasheetUrl": "https://www.st.com/...",
    "PhotoUrl": "https://mm.digikey.com/...",
    "ProductStatus": {"Id": 1, "Status": "Active"},
    "Category": {"CategoryId": 771, "Name": "Microcontrollers", "ChildCategories": []},
    "Parameters": [
        {"ParameterId": 1, "ParameterText": "Core Processor", "ValueText": "ARM Cortex-M4"},
    ],
    "ProductVariations": [
        {
            "DigiKeyProductNumber": "497-19657-1-ND",
            "PackageType": {"Id": 2, "Name": "Cut Tape (CT)"},
            "StandardPricing": [
                {"BreakQuantity": 1, "UnitPrice": 10.49, "TotalPrice": 10.49},
                {"BreakQuantity": 10, "UnitPrice": 8.2, "TotalPrice": 82.0},
            ],
            "QuantityAvailableforPackageType": 3648,
            "MinimumOrderQuantity": 1,
            "StandardPackage": 0,
        }
    ],
}


class TestManufacturer:
    def test_from_dict(self):
        mfr = Manufacturer.from_dict({"Id": 497, "Name": "STMicroelectronics"})
        assert mfr.id == 497
        assert mfr.name == "STMicroelectronics"

    def test_from_dict_empty(self):
        mfr = Manufacturer.from_dict({})
        assert mfr.id == 0
        assert mfr.name == ""

    def test_raw_data_preserved(self):
        data = {"Id": 1, "Name": "Test", "Extra": "field"}
        mfr = Manufacturer.from_dict(data)
        assert mfr.raw_data == data


class TestCategory:
    def test_from_dict(self):
        cat = Category.from_dict({"CategoryId": 771, "Name": "Microcontrollers", "ChildCategories": []})
        assert cat.id == 771
        assert cat.name == "Microcontrollers"
        assert cat.children == []

    def test_from_dict_with_children(self):
        data = {
            "CategoryId": 1,
            "Name": "Parent",
            "ChildCategories": [
                {"CategoryId": 2, "Name": "Child1", "ChildCategories": []},
                {"CategoryId": 3, "Name": "Child2", "ChildCategories": []},
            ],
        }
        cat = Category.from_dict(data)
        assert len(cat.children) == 2
        assert cat.children[0].id == 2
        assert cat.children[1].name == "Child2"


class TestParameter:
    def test_from_dict(self):
        param = Parameter.from_dict(
            {"ParameterId": 1, "ParameterText": "Core Processor", "ValueText": "ARM Cortex-M4"}
        )
        assert param.parameter_id == 1
        assert param.name == "Core Processor"
        assert param.value == "ARM Cortex-M4"


class TestPriceBreak:
    def test_from_dict(self):
        pb = PriceBreak.from_dict(
            {"BreakQuantity": 10, "UnitPrice": 8.2, "TotalPrice": 82.0}
        )
        assert pb.break_quantity == 10
        assert pb.unit_price == 8.2
        assert pb.total_price == 82.0


class TestProductVariation:
    def test_from_dict(self):
        data = SAMPLE_PRODUCT_DATA["ProductVariations"][0]
        pv = ProductVariation.from_dict(data)
        assert pv.digi_key_product_number == "497-19657-1-ND"
        assert pv.package_type == "Cut Tape (CT)"
        assert len(pv.standard_pricing) == 2
        assert pv.standard_pricing[0].unit_price == 10.49
        assert pv.quantity_available == 3648
        assert pv.min_order_quantity == 1
        assert pv.raw_data == data


class TestProduct:
    def test_from_dict(self):
        product = Product.from_dict(SAMPLE_PRODUCT_DATA)
        assert product.manufacturer_product_number == "STM32F407VET6TR"
        assert product.manufacturer.id == 497
        assert product.manufacturer.name == "STMicroelectronics"
        assert product.description == "IC MCU 32BIT 512KB FLASH 100LQFP"
        assert "ARM Cortex-M4" in product.detailed_description
        assert product.unit_price == 10.49
        assert "digikey.com" in product.product_url
        assert product.datasheet_url == "https://www.st.com/..."
        assert product.photo_url == "https://mm.digikey.com/..."
        assert product.product_status == "Active"

    def test_from_dict_category(self):
        product = Product.from_dict(SAMPLE_PRODUCT_DATA)
        assert product.category is not None
        assert product.category.id == 771
        assert product.category.name == "Microcontrollers"

    def test_from_dict_parameters(self):
        product = Product.from_dict(SAMPLE_PRODUCT_DATA)
        assert len(product.parameters) == 1
        assert product.parameters[0].name == "Core Processor"

    def test_from_dict_variations(self):
        product = Product.from_dict(SAMPLE_PRODUCT_DATA)
        assert len(product.product_variations) == 1
        assert product.product_variations[0].digi_key_product_number == "497-19657-1-ND"
        assert len(product.product_variations[0].standard_pricing) == 2

    def test_from_dict_raw_data_preserved(self):
        product = Product.from_dict(SAMPLE_PRODUCT_DATA)
        assert product.raw_data == SAMPLE_PRODUCT_DATA

    def test_from_dict_no_category(self):
        data = {**SAMPLE_PRODUCT_DATA, "Category": None}
        product = Product.from_dict(data)
        assert product.category is None

    def test_from_dict_product_status_string(self):
        # ProductStatus가 문자열인 경우
        data = {**SAMPLE_PRODUCT_DATA, "ProductStatus": "Obsolete"}
        product = Product.from_dict(data)
        assert product.product_status == "Obsolete"
