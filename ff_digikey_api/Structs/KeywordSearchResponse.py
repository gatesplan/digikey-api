from dataclasses import dataclass, field

from ff_digikey_api.Structs.Product import Product


@dataclass
class KeywordSearchResponse:
    products: list[Product] = field(default_factory=list)
    products_count: int = 0
    exact_matches: list[Product] = field(default_factory=list)
    filter_options: dict = field(default_factory=dict)
    raw_data: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "KeywordSearchResponse":
        products = [Product.from_dict(p) for p in data.get("Products", [])]
        exact = [Product.from_dict(p) for p in data.get("ExactMatches", [])]
        return cls(
            products=products,
            products_count=data.get("ProductsCount", 0),
            exact_matches=exact,
            filter_options=data.get("FilterOptions", {}),
            raw_data=data,
        )
