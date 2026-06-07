from dataclasses import dataclass, field


@dataclass
class Manufacturer:
    id: int
    name: str
    raw_data: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Manufacturer":
        return cls(id=data.get("Id", 0), name=data.get("Name", ""), raw_data=data)
