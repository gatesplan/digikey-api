from __future__ import annotations

import operator as op_module

from ff_digikey_api.Util.ParametricExpression import ParametricExpression
from ff_digikey_api.Util.ValueParser import parse_numeric_value

_NUMERIC_OPS = {
    ">": op_module.gt,
    ">=": op_module.ge,
    "<": op_module.lt,
    "<=": op_module.le,
    "=": op_module.eq,
    "!=": op_module.ne,
}


def _find_parameter(
    name: str, parametric_filters: list[dict]
) -> dict:
    name_lower = name.lower()

    # 1) 정확 매칭
    for pf in parametric_filters:
        if pf["ParameterName"].lower() == name_lower:
            return pf

    # 2) startswith 매칭
    candidates = [
        pf for pf in parametric_filters
        if pf["ParameterName"].lower().startswith(name_lower)
    ]
    if len(candidates) == 1:
        return candidates[0]

    # 3) contains 매칭
    if not candidates:
        candidates = [
            pf for pf in parametric_filters
            if name_lower in pf["ParameterName"].lower()
        ]
    if len(candidates) == 1:
        return candidates[0]

    if not candidates:
        raise ValueError(
            f"parameter not found: {name!r}"
        )
    names = [c["ParameterName"] for c in candidates]
    raise ValueError(
        f"ambiguous parameter {name!r}, candidates: {names}"
    )


def _match_single(
    expr: ParametricExpression, parametric_filters: list[dict]
) -> dict:
    param = _find_parameter(expr.param_name, parametric_filters)
    matched_ids = []

    for fv in param.get("FilterValues", []):
        value_name = fv.get("ValueName", "")
        value_id = fv.get("ValueId", "")

        if expr.operator in (">", ">=", "<", "<="):
            # 숫자 비교만
            parsed = parse_numeric_value(value_name)
            if parsed is None or expr.numeric_value is None:
                continue
            cmp = _NUMERIC_OPS[expr.operator]
            if cmp(parsed, expr.numeric_value):
                matched_ids.append(value_id)

        elif expr.operator == "=":
            if expr.numeric_value is not None:
                parsed = parse_numeric_value(value_name)
                if parsed is not None and parsed == expr.numeric_value:
                    matched_ids.append(value_id)
            else:
                if value_name.lower() == expr.raw_value.lower():
                    matched_ids.append(value_id)

        elif expr.operator == "!=":
            if expr.numeric_value is not None:
                # 파싱 불가(None) 값은 제외한다. '=' 분기와 대칭.
                parsed = parse_numeric_value(value_name)
                if parsed is not None and parsed != expr.numeric_value:
                    matched_ids.append(value_id)
            else:
                if value_name.lower() != expr.raw_value.lower():
                    matched_ids.append(value_id)

    return {
        "parameter_id": param["ParameterId"],
        "value_ids": matched_ids,
    }


def match_filters(
    expressions: list[ParametricExpression],
    parametric_filters: list[dict],
) -> list[dict]:
    return [_match_single(expr, parametric_filters) for expr in expressions]
