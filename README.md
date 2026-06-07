# ff-digikey-api

DigiKey V4 API Python 클라이언트. AI 에이전트가 부품 검색/조회를 편리하게 할 수 있도록 설계되었습니다.

## DigiKey V4 API의 문제점

패키지 제작자의 말에 따르면 "진짜 개병신같은 API"라고 합니다.

DigiKey V4 API의 검색 엔드포인트는 웹 UI의 각 select 메뉴 ID를 그대로 전달하는 방식이고, Mouser의 `>15ohm` 같은 직관적인 파라미터 검색을 지원하지 않습니다. 구체적으로:

1. **ID 기반 필터링만 지원** -- `>15ohm` 같은 범위 검색이 불가능합니다. 웹 UI 드롭다운 메뉴 각 항목의 내부 ID(ParameterId + ValueId)를 정확히 알아서 전달해야 합니다. select 메뉴가 잘 안 바뀌는 것이 그나마 다행입니다.
2. **파라미터 목록 조회 API 없음** -- 사용 가능한 필터 ID를 알려면 먼저 검색을 실행하고 응답의 `FilterOptions.ParametricFilters`에서 추출해야 합니다. 그런데 이마저도 `CategoryFilter`를 명시해야만 반환됩니다.
3. **카테고리 필수** -- 파라미터 필터는 리프 카테고리 ID가 필요합니다. 검색 결과의 제품에는 루트 카테고리만 포함되어 있어서, `ChildCategories`를 파고 들어가 리프 ID를 찾아야 합니다.
4. **결과적으로 3단계 API 호출** -- (1) 검색해서 카테고리 추출 (2) 카테고리로 재검색해서 파라미터 필터 목록 수집 (3) 원하는 값의 ID를 골라 최종 검색. 단순한 "10kohm 이상 저항기" 검색에 API 3회 호출이 필요합니다.
5. **비영어 로케일 불안정** -- 미국 회사답게 영어 외 로케일의 파라미터명/값 번역이 일관성이 없습니다. 영어 로케일 사용을 강력히 권장합니다.

## 이 패키지의 개선

이 패키지는 위의 불편함을 에이전트가 신경 쓸 필요 없도록 내부적으로 처리합니다:

- **범위 표현식 지원**: `Resistance>10kohm`, `Tolerance<=1%` 같은 표현식을 파싱하여 자동으로 매칭되는 ValueId를 찾아 필터링합니다.
- **SI 접두사 처리**: `4.7uF`, `100nF`, `1.5kohm` 등 SI 접두사를 자동 변환하여 DigiKey의 값(e.g. "1.5 kOhms")과 비교합니다.
- **카테고리 자동 감지**: 키워드 검색 결과에서 리프 카테고리를 자동 추출합니다. 직접 지정도 가능합니다.
- **MCP 서버 제공**: AI 에이전트가 `digikey_usage()` 도구를 호출하면 전체 사용법이 나오고, `digikey_params()` -> `digikey_parametric_search()` 순서로 바로 활용할 수 있습니다.

## 주요 기능

- OAuth 2.0 인증 + 토큰 자동 갱신
- `>15ohm`, `<=1%` 같은 범위 검색 표현식 (Mouser 스타일)
- MCP 서버로 Claude Code 등 AI 에이전트에서 직접 호출
- 영어 로케일 기본 (가장 안정적), 다국어 로케일 선택 가능

## Quick Start

### 1. 설치

```bash
pip install ff-digikey-api
```

### 2. DigiKey 개발자 등록

1. [DigiKey API Portal](https://developer.digikey.com/)에서 앱 생성
2. **Product Information V4** API를 구독
3. Client ID / Client Secret 발급 (2-legged OAuth라 Callback URL 설정 불필요)

### 3. 환경변수 설정

`.env` 파일 생성:

```
DIGIKEY_CLIENT_ID=your_client_id
DIGIKEY_CLIENT_SECRET=your_client_secret
DIGIKEY_LANGUAGE=ko
DIGIKEY_CURRENCY=KRW
DIGIKEY_SITE=KR
```

### 4. 사용

```python
from ff_digikey_api import DigiKeyClient

client = DigiKeyClient.from_env(".env")

# 부품 검색 (토큰은 client_credentials로 자동 발급/갱신, 브라우저 불필요)
result = client.search("STM32F407", limit=5)
for p in result.products:
    print(p.manufacturer_product_number, p.unit_price, "KRW")

client.close()
```

> 인증은 2-legged OAuth(client_credentials)입니다. 브라우저/로그인 없이
> Client ID/Secret만으로 토큰이 자동 발급되며, 만료(약 10분)시 자동 재발급됩니다.
> `authorize()` 호출은 선택사항(자격증명 사전검증)입니다.

---

## 초기화

### 직접 전달

```python
from ff_digikey_api import DigiKeyClient, DigiKeyLocale

client = DigiKeyClient(
    client_id="...",
    client_secret="...",
    locale=DigiKeyLocale(language="ko", currency="KRW", site="KR"),
)
```

### 환경변수

```python
client = DigiKeyClient.from_env(".env")
```

### Context Manager

```python
with DigiKeyClient.from_env(".env") as client:
    result = client.search("LM358")
```

### 옵션

| 파라미터 | 기본값 | 설명 |
|---------|--------|------|
| `sandbox` | `False` | Sandbox API 사용 |
| `storage_path` | `"token_storage.json"` | 토큰 저장 파일 경로 (캐시) |

---

## API Reference

### `authorize()`

client_credentials(2-legged) 토큰을 발급/저장합니다. 브라우저/로그인이 없습니다.
호출은 **선택사항**입니다 -- 모든 API 호출이 토큰을 lazy 발급하며, 만료시 자동 재발급합니다.
주로 자격증명(Client ID/Secret) 사전검증 용도로 사용합니다.

```python
client.authorize()  # 선택: 자격증명이 유효한지 미리 확인
```

---

### `search(keywords, limit, offset, filters, sort)`

키워드로 부품을 검색합니다.

**Input**

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `keywords` | `str` | (필수) | 검색 키워드 |
| `limit` | `int` | `10` | 반환 개수 (1~50으로 클램프) |
| `offset` | `int` | `0` | 페이지 오프셋 |
| `filters` | `FilterOptions` | `None` | 필터 (제조사, 카테고리 등) |
| `sort` | `SortOptions` | `None` | 정렬 옵션 |

**Output** — `KeywordSearchResponse`

| 필드 | 타입 | 설명 |
|------|------|------|
| `products` | `list[Product]` | 검색 결과 목록 |
| `products_count` | `int` | 전체 결과 수 |
| `exact_matches` | `list[Product]` | 정확히 일치하는 결과 |
| `filter_options` | `dict` | 사용 가능한 필터 옵션 |
| `raw_data` | `dict` | API 원본 응답 |

**예시**

```python
from ff_digikey_api import FilterOptions, SortOptions

# 기본 검색
result = client.search("STM32F407", limit=10)
print(f"총 {result.products_count}건")
for p in result.products:
    print(f"{p.manufacturer_product_number} | {p.manufacturer.name} | {p.unit_price} KRW")

# 필터 + 정렬
result = client.search(
    "capacitor 100uF",
    limit=10,
    filters=FilterOptions(manufacturer_ids=[13]),
    sort=SortOptions(field="UnitPrice", sort_order="Ascending"),
)
```

---

### `parametric_search(keywords, expressions, ...)`

2단계 검색: 먼저 필터 옵션을 조회한 후, 파라미터 필터를 적용하여 재검색합니다.
Mouser의 `>15ohm` 스타일 검색을 DigiKey API 위에서 구현한 기능입니다.

**Input**

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `keywords` | `str` | (필수) | 검색 키워드 |
| `expressions` | `list[str] \| str` | (필수) | 필터 표현식 |
| `limit` | `int` | `10` | 반환 개수 (1~50으로 클램프) |
| `offset` | `int` | `0` | 페이지 오프셋 |
| `filters` | `FilterOptions` | `None` | 추가 필터 |
| `sort` | `SortOptions` | `None` | 정렬 옵션 |
| `category_id` | `int` | `None` | 카테고리 ID (None이면 자동 감지) |

**표��식 문법**

| 연산자 | 의미 | 예시 |
|--------|------|------|
| `>` | 초과 | `Resistance>15ohm` |
| `>=` | 이상 | `Voltage>=3.3V` |
| `<` | 미만 | `Current<20mA` |
| `<=` | 이하 | `Tolerance<=1%` |
| `=` | 일치 | `Color=Green` |
| `!=` | 불일치 | `Color!=Red` |

SI 접두사: `p`(pico), `n`(nano), `u`(micro), `m`(milli), `k`(kilo), `M`(mega), `G`(giga)

**Output** -- `KeywordSearchResponse` (search와 동일)

**예시**

```python
# 15옴 초과 저항기 검색
result = client.parametric_search(
    "resistor",
    expressions=["Resistance>15ohm", "Tolerance<=1%"],
    limit=10,
)
for p in result.products:
    print(f"{p.manufacturer_product_number} | {p.unit_price} KRW")

# 단일 표현식 (문자열로도 가능)
result = client.parametric_search("LED", "Color=Green")

# 카테고리 직접 지정
result = client.parametric_search(
    "capacitor",
    ["Capacitance>=100uF"],
    category_id=58,
)
```

---

### `product_details(product_number)`

제조사 부품번호(MPN)로 상세 정보를 조회합니다.

**Input**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `product_number` | `str` | 제조사 부품번호 |

**Output** — `Product`

| 필드 | 타입 | 설명 |
|------|------|------|
| `manufacturer_product_number` | `str` | MPN |
| `manufacturer` | `Manufacturer` | 제조사 (`.id`, `.name`) |
| `description` | `str` | 짧은 설명 |
| `detailed_description` | `str` | 상세 설명 |
| `unit_price` | `float` | 단가 |
| `product_url` | `str` | DigiKey 제품 페이지 URL |
| `datasheet_url` | `str \| None` | 데이터시트 URL |
| `photo_url` | `str \| None` | 제품 이미지 URL |
| `product_status` | `str` | 상태 (Active, Obsolete 등) |
| `category` | `Category \| None` | 카테고리 (`.id`, `.name`, `.children`) |
| `parameters` | `list[Parameter]` | 사양 목록 (`.name`, `.value`) |
| `product_variations` | `list[ProductVariation]` | 포장 변형 목록 |
| `raw_data` | `dict` | API 원본 응답 |

`ProductVariation` 필드:

| 필드 | 타입 | 설명 |
|------|------|------|
| `digi_key_product_number` | `str` | DigiKey 부품번호 |
| `package_type` | `str` | 포장 타입 (Cut Tape, Tape & Reel 등) |
| `standard_pricing` | `list[PriceBreak]` | 수량별 단가 |
| `quantity_available` | `int` | 재고 수량 |
| `min_order_quantity` | `int` | 최소 주문 수량 |

`PriceBreak` 필드: `break_quantity`, `unit_price`, `total_price`

**예시**

```python
detail = client.product_details("STM32F407VET6TR")
print(f"{detail.manufacturer_product_number} - {detail.description}")
print(f"제조사: {detail.manufacturer.name}")
print(f"상태: {detail.product_status}")
print(f"카테고리: {detail.category.name}")

for param in detail.parameters:
    print(f"  {param.name}: {param.value}")

for v in detail.product_variations:
    print(f"  {v.digi_key_product_number} | 재고: {v.quantity_available}")
    for pb in v.standard_pricing:
        print(f"    {pb.break_quantity}개: {pb.unit_price} KRW")
```

---

### `pricing(product_number)`

부품의 가격 정보만 조회합니다.

**Input**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `product_number` | `str` | 제조사 부품번호 |

**Output** — `ProductPricingResponse`

| 필드 | 타입 | 설명 |
|------|------|------|
| `products` | `list[Product]` | 가격 정보가 포함된 제품 목록 |
| `products_count` | `int` | 결과 수 |
| `raw_data` | `dict` | API 원본 응답 |

**예시**

```python
pricing = client.pricing("STM32F407VET6TR")
for p in pricing.products:
    for v in p.product_variations:
        print(f"{v.digi_key_product_number} ({v.package_type})")
        for pb in v.standard_pricing:
            print(f"  {pb.break_quantity}개: {pb.unit_price} KRW")
```

---

### `associations(product_number)`

연관 부품 목록을 조회합니다.

**Input**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `product_number` | `str` | 제조사 부품번호 |

**Output** — `list[Product]`

**예시**

```python
assocs = client.associations("STM32F407VET6TR")
for p in assocs:
    print(f"{p.manufacturer_product_number} | {p.description}")
```

---

### `substitutions(product_number)`

대체 가능한 부품 목록을 조회합니다.

**Input**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `product_number` | `str` | 제조사 부품번호 |

**Output** — `list[Product]`

**예시**

```python
subs = client.substitutions("STM32F407VET6TR")
for p in subs:
    print(f"{p.manufacturer_product_number} | {p.manufacturer.name}")
```

---

### `recommended_products(product_number)`

추천 부품 목록을 조회합니다.

**Input**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `product_number` | `str` | 제조사 부품번호 |

**Output** — `list[Product]`

**예시**

```python
recs = client.recommended_products("STM32F407VET6TR")
for p in recs:
    print(f"{p.manufacturer_product_number} | {p.unit_price} KRW")
```

---

### `alternate_packaging(product_number)`

동일 부품의 다른 포장 형태를 조회합니다.

**Input**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `product_number` | `str` | 제조사 부품번호 |

**Output** — `list[Product]`

**예시**

```python
alts = client.alternate_packaging("STM32F407VET6TR")
for p in alts:
    for v in p.product_variations:
        print(f"{v.digi_key_product_number} | {v.package_type} | 재고: {v.quantity_available}")
```

---

### `media(product_number)`

부품의 미디어 리소스(이미지, 동영상 등)를 조회합니다.

**Input**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `product_number` | `str` | 제조사 부품번호 |

**Output** — `dict` (API 원본 응답)

**예시**

```python
media = client.media("STM32F407VET6TR")
for link in media.get("MediaLinks", []):
    print(f"{link['MediaType']}: {link['Url']}")
```

---

### `manufacturers()`

DigiKey에 등록된 전체 제조사 목록을 조회합니다.

**Input** — 없음

**Output** — `list[Manufacturer]`

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | `int` | 제조사 ID |
| `name` | `str` | 제조사 이름 |

**예시**

```python
mfrs = client.manufacturers()
for m in mfrs[:10]:
    print(f"[{m.id}] {m.name}")
```

---

### `categories()`

전체 카테고리 트리를 조회합니다.

**Input** — 없음

**Output** — `list[Category]`

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | `int` | 카테고리 ID |
| `name` | `str` | 카테고리 이름 |
| `children` | `list[Category]` | 하위 카테고리 |

**예시**

```python
cats = client.categories()
for c in cats[:5]:
    print(f"[{c.id}] {c.name}")
    for child in c.children[:3]:
        print(f"  └ [{child.id}] {child.name}")
```

---

## 에러 처리

```python
from ff_digikey_api.Core.HttpClient.ApiError import ApiError
from ff_digikey_api.Core.HttpClient.RateLimitError import RateLimitError
from ff_digikey_api.Service.TokenManager.TokenExpiredError import TokenExpiredError

try:
    result = client.search("STM32")
except RateLimitError as e:
    print(f"요청 한도 초과. {e.retry_after}초 후 재시도")
except TokenExpiredError:
    print("자격증명 무효. DIGIKEY_CLIENT_ID/SECRET 확인 필요")
except ApiError as e:
    print(f"API 에러 [{e.status_code}]: {e.message}")
```

## 모든 Struct에 `raw_data`

모든 응답 객체는 `raw_data` 필드에 API 원본 JSON을 보존합니다.
라이브러리가 파싱하지 않는 필드가 필요하면 `raw_data`에서 직접 접근할 수 있습니다.

```python
detail = client.product_details("STM32F407VET6TR")
# 라이브러리가 파싱하지 않는 필드
print(detail.raw_data["QuantityAvailable"])
print(detail.raw_data["ManufacturerLeadWeeks"])
```

## CLI (Agent-Oriented)

이 패키지는 Python API 라이브러리이면서, 주로 **AI 에이전트가 콘솔에서 DigiKey 부품 정보를 조회**하기 위해 만들어졌습니다.
설치 후 `ff-digikey` 명령으로 바로 사용할 수 있으며, 모든 출력은 에이전트가 파싱하기 쉬운 JSON 형식입니다.

```bash
pip install ff-digikey-api
```

### 인증 (선택)

```bash
ff-digikey authorize
```

client_credentials로 토큰을 발급/캐시합니다(브라우저 없음). 생략해도 각 명령이
토큰을 자동 발급하므로, 이 명령은 자격증명 사전검증 용도입니다.

### 부품 검색

```bash
ff-digikey search "STM32F407" --limit 5
ff-digikey search "capacitor 100uF" --limit 10 --offset 0

# 파라미터 필터 검색 (-p 옵션, 복수 지정 가능)
ff-digikey search "resistor" -p "Resistance>15ohm" -p "Tolerance<=1%"
ff-digikey search "LED" -p "Color=Green"
```

### 파라미터 필터 목록 조회

```bash
ff-digikey params "resistor"           # 키워드로 카테고리 자동추출
ff-digikey params --category 52        # 카테고리 ID 직접 지정
```

### 부품 상세 조회

```bash
ff-digikey details STM32F407VET6TR
```

### 가격 조회

```bash
ff-digikey pricing STM32F407VET6TR
```

### 에러 처리

에러 발생 시 stderr로 JSON 에러 객체가 출력되고 exit code 1로 종료됩니다.

```json
{"error": "TokenExpiredError", "message": "Invalid client credentials. Check DIGIKEY_CLIENT_ID/DIGIKEY_CLIENT_SECRET."}
```

## MCP Server (AI Agent Integration)

AI 에이전트(Claude Code 등)가 DigiKey API를 MCP 도구로 직접 호출할 수 있습니다.

### 설치

```bash
pip install ff-digikey-api[mcp]
```

### 인증

client_credentials(2-legged) 방식이라 사전 인증 단계가 필요 없습니다. MCP 서버는
첫 도구 호출 시 Client ID/Secret로 토큰을 자동 발급합니다(브라우저/헤드리스 행 없음).

### MCP 설정

프로젝트의 `.mcp.json` 또는 Claude Code 설정에 추가:

```json
{
  "mcpServers": {
    "digikey": {
      "command": "python",
      "args": ["-m", "ff_digikey_api.mcp_wrapper"],
      "env": {
        "DIGIKEY_CLIENT_ID": "your_client_id",
        "DIGIKEY_CLIENT_SECRET": "your_client_secret"
      }
    }
  }
}
```

> 기본 로케일은 영어(en/USD/US)입니다. 영어 권장 -- 파라미터명과 필터값이 영어일 때 가장 안정적입니다.
> 한국어 등 다른 로케일이 필요하면 env에 `DIGIKEY_LANGUAGE`, `DIGIKEY_CURRENCY`, `DIGIKEY_SITE`를 추가하세요.

또는 CLI로 등록:

```bash
claude mcp add digikey -- python -m ff_digikey_api.mcp_wrapper
```

### 제공 도구

| 도구 | 설명 |
|------|------|
| `digikey_usage` | 전체 사용법 가이드 반환. 에이전트가 처음 호출. |
| `digikey_search` | 키워드 검색 |
| `digikey_params` | 파라미터 필터 이름/값 목록 조회 (parametric_search 전에 호출) |
| `digikey_parametric_search` | 파라미터 표현식으로 필터 검색 |
| `digikey_details` | MPN으로 상세 조회 |
| `digikey_pricing` | 가격/재고 조회 |

에이전트 사용 흐름: `digikey_usage()` -> `digikey_params("resistor")` -> `digikey_parametric_search("resistor", "Resistance>10kohm")`

## License

MIT
