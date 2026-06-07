from dataclasses import dataclass, field

from ff_digikey_api.Structs.PriceBreak import PriceBreak


@dataclass
class ProductVariation:
    digi_key_product_number: str
    package_type: str
    standard_pricing: list[PriceBreak] = field(default_factory=list)
    quantity_available: int = 0
    min_order_quantity: int = 0
    standard_package: int = 0
    raw_data: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "ProductVariation":
        pricing = [PriceBreak.from_dict(p) for p in data.get("StandardPricing", [])]
        pkg = data.get("PackageType", {})
        return cls(
            digi_key_product_number=data.get("DigiKeyProductNumber", ""),
            package_type=pkg.get("Name", ""),
            standard_pricing=pricing,
            quantity_available=data.get("QuantityAvailableforPackageType", 0),
            min_order_quantity=data.get("MinimumOrderQuantity", 0),
            standard_package=data.get("StandardPackage", 0),
            raw_data=data,
        )
