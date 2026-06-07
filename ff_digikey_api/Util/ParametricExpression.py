from __future__ import annotations

import re
from dataclasses import dataclass

from ff_digikey_api.Util.ValueParser import parse_numeric_value


@dataclass
class ParametricExpression:
    param_name: str
    operator: str
    raw_value: str
    numeric_value: float | None


_EXPR_PATTERN = re.compile(r"^(.+?)(!=|>=|<=|>|<|=)(.+)$")


def parse_expression(expr: str) -> ParametricExpression:
    if not expr or not expr.strip():
        raise ValueError("empty expression")

    m = _EXPR_PATTERN.match(expr.strip())
    if not m:
        raise ValueError(f"invalid expression: {expr!r}")

    name, op, value = m.group(1).strip(), m.group(2), m.group(3).strip()
    return ParametricExpression(
        param_name=name,
        operator=op,
        raw_value=value,
        numeric_value=parse_numeric_value(value),
    )
