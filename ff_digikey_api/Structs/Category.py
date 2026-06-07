from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Category:
    id: int
    name: str
    children: list[Category] = field(default_factory=list)
    raw_data: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> Category:
        children = [cls.from_dict(c) for c in data.get("ChildCategories", [])]
        return cls(
            id=data.get("CategoryId", data.get("Id", 0)),
            name=data.get("Name", ""),
            children=children,
            raw_data=data,
        )
