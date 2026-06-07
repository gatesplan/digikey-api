from __future__ import annotations

from dataclasses import dataclass, field

from ff_digikey_api.Structs.Manufacturer import Manufacturer
from ff_digikey_api.Structs.Category import Category
from ff_digikey_api.Structs.Parameter import Parameter
from ff_digikey_api.Structs.ProductVariation import ProductVariation


@dataclass
class Product:
    manufacturer_product_number: str
    manufacturer: Manufacturer
    description: str
    detailed_description: str
    unit_price: float
    product_url: str
    datasheet_url: str | None = None
    photo_url: str | None = None
    product_status: str = ""
    category: Category | None = None
    parameters: list[Parameter] = field(default_factory=list)
    product_variations: list[ProductVariation] = field(default_factory=list)
    raw_data: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        # API 응답의 PascalCase -> snake_case 변환
        desc = data.get("Description", {})
        mfr = Manufacturer.from_dict(data.get("Manufacturer", {}))
        cat = Category.from_dict(data["Category"]) if data.get("Category") else None
        params = [Parameter.from_dict(p) for p in data.get("Parameters", [])]
        variations = [ProductVariation.from_dict(v) for v in data.get("ProductVariations", [])]

        # ProductStatus는 dict 또는 str일 수 있음
        ps = data.get("ProductStatus")
        if isinstance(ps, dict):
            product_status = ps.get("Status", "")
        else:
            product_status = str(ps) if ps is not None else ""

        return cls(
            manufacturer_product_number=data.get("ManufacturerProductNumber", ""),
            manufacturer=mfr,
            description=desc.get("ProductDescription", ""),
            detailed_description=desc.get("DetailedDescription", ""),
            unit_price=data.get("UnitPrice", 0.0),
            product_url=data.get("ProductUrl", ""),
            datasheet_url=data.get("DatasheetUrl"),
            photo_url=data.get("PhotoUrl"),
            product_status=product_status,
            category=cat,
            parameters=params,
            product_variations=variations,
            raw_data=data,
        )
