from dataclasses import dataclass, field


@dataclass
class PriceBreak:
    break_quantity: int
    unit_price: float
    total_price: float
    raw_data: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "PriceBreak":
        return cls(
            break_quantity=data.get("BreakQuantity", 0),
            unit_price=data.get("UnitPrice", 0.0),
            total_price=data.get("TotalPrice", 0.0),
            raw_data=data,
        )
