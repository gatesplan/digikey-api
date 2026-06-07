from dataclasses import dataclass, field


@dataclass
class Parameter:
    parameter_id: int
    name: str
    value: str
    raw_data: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Parameter":
        return cls(
            parameter_id=data.get("ParameterId", 0),
            name=data.get("ParameterText", ""),
            value=data.get("ValueText", ""),
            raw_data=data,
        )
