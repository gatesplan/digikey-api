from __future__ import annotations

import re

_SI_PREFIX = {
    "p": 1e-12,
    "n": 1e-9,
    "u": 1e-6,
    "\u00b5": 1e-6,
    "m": 1e-3,
    "k": 1e3,
    "K": 1e3,
    "M": 1e6,
    "G": 1e9,
    "T": 1e12,
}

_PATTERN = re.compile(
    r"^\s*([+-]?\d+\.?\d*)\s*([pnumkKMGT\u00b5]?)(.*)$"
)


def parse_numeric_value(text: str) -> float | None:
    if not text or not text.strip():
        return None

    text = text.strip()
    # 공차/온도계수 등의 +/- 기호(U+00B1) 제거. "+/-1%" -> "1%"
    text = text.lstrip("\u00b1")
    # % -> 숫자 부분만 추출
    if text.endswith("%"):
        text = text[:-1]

    m = _PATTERN.match(text)
    if not m:
        return None

    number_str, prefix, rest = m.groups()
    value = float(number_str)
    # SI 배율은 접두사 뒤에 단위가 있을 때만 적용한다.
    # 그래야 "3000K"(켈빈), "1.4 T"(테슬라), "5G"(가우스)처럼 접두사 글자가
    # 사실은 단위인 경우를 1e3~1e12로 잘못 곱하지 않는다.
    # ("10kOhm", "100mV" 등 실제 접두사는 뒤에 단위가 오므로 정상 적용)
    if prefix and rest.strip():
        value *= _SI_PREFIX.get(prefix, 1.0)
    return value
