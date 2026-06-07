from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ParameterFilter:
    parameter_id: int
    value_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "ParameterId": self.parameter_id,
            "FilterValues": [{"Id": vid} for vid in self.value_ids],
        }


@dataclass
class ParametricFilterRequest:
    parameter_filters: list[ParameterFilter] = field(default_factory=list)
    category_id: int | None = None

    def to_dict(self) -> dict:
        result = {
            "ParameterFilters": [pf.to_dict() for pf in self.parameter_filters],
        }
        if self.category_id is not None:
            result["CategoryFilter"] = {"Id": str(self.category_id)}
        return result

    @classmethod
    def from_match_results(
        cls, matches: list[dict], category_id: int | None = None
    ) -> ParametricFilterRequest:
        filters = [
            ParameterFilter(
                parameter_id=m["parameter_id"],
                value_ids=m["value_ids"],
            )
            for m in matches
        ]
        return cls(parameter_filters=filters, category_id=category_id)
