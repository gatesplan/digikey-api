from dataclasses import dataclass


@dataclass
class SortOptions:
    field: str = "None"
    sort_order: str = "Ascending"

    def to_dict(self) -> dict:
        return {"Field": self.field, "SortOrder": self.sort_order}
