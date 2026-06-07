from __future__ import annotations

from dataclasses import dataclass, field

from ff_digikey_api.Structs.ParametricFilterRequest import ParametricFilterRequest


@dataclass
class FilterOptions:
    manufacturer_ids: list[int] = field(default_factory=list)
    category_ids: list[int] = field(default_factory=list)
    status_ids: list[int] = field(default_factory=list)
    packaging_ids: list[int] = field(default_factory=list)
    marketplace: bool | None = None
    parametric_filter: ParametricFilterRequest | None = None

    def to_dict(self) -> dict:
        result = {}
        if self.manufacturer_ids:
            result["ManufacturerFilter"] = [{"Id": str(i)} for i in self.manufacturer_ids]
        if self.category_ids:
            result["CategoryFilter"] = [{"Id": str(i)} for i in self.category_ids]
        if self.status_ids:
            result["StatusFilter"] = [{"Id": str(i)} for i in self.status_ids]
        if self.packaging_ids:
            result["PackagingFilter"] = [{"Id": str(i)} for i in self.packaging_ids]
        if self.marketplace is not None:
            if self.marketplace:
                result["MarketPlaceFilter"] = "MarketPlaceOnly"
            else:
                result["MarketPlaceFilter"] = "ExcludeMarketPlace"
        if self.parametric_filter is not None:
            result["ParameterFilterRequest"] = self.parametric_filter.to_dict()
        return result
