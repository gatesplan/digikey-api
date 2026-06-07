from __future__ import annotations

from dataclasses import dataclass

from ff_digikey_api.Structs.FilterOptions import FilterOptions
from ff_digikey_api.Structs.SortOptions import SortOptions


@dataclass
class KeywordSearchRequest:
    keywords: str
    limit: int = 50
    offset: int = 0
    filters: FilterOptions | None = None
    sort: SortOptions | None = None

    def to_dict(self) -> dict:
        result = {
            "Keywords": self.keywords,
            "Limit": self.limit,
            "Offset": self.offset,
        }
        if self.filters:
            result["FilterOptionsRequest"] = self.filters.to_dict()
        if self.sort:
            result["SortOptions"] = self.sort.to_dict()
        return result
