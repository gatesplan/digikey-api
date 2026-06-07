from dataclasses import dataclass, field

from ff_digikey_api.Structs.Product import Product


@dataclass
class ProductPricingResponse:
    products: list[Product] = field(default_factory=list)
    products_count: int = 0
    raw_data: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "ProductPricingResponse":
        items = data.get("ProductPricings", data.get("Products", []))
        products = [Product.from_dict(p) for p in items]
        # /pricing 응답 항목에는 top-level UnitPrice가 없어 0.0이 된다.
        # 변형의 첫 수량브레이크 단가로 대표 단가를 보정한다.
        for p in products:
            if not p.unit_price and p.product_variations:
                breaks = p.product_variations[0].standard_pricing
                if breaks:
                    p.unit_price = breaks[0].unit_price
        return cls(
            products=products,
            products_count=data.get("ProductsCount", len(products)),
            raw_data=data,
        )
