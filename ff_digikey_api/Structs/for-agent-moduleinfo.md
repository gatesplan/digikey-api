# Structs
DigiKey API 데이터 구조체 모듈. Constants 모듈 의존 (Tier 0).
모든 구조체는 `@dataclass` 기반. API 응답의 PascalCase를 snake_case로 변환.

## DigiKeyConfig
API 클라이언트 설정. client_id, client_secret, sandbox 모드 등.

## DigiKeyLocale
로케일 설정 (language, currency, site). `to_headers()`로 헤더 딕셔너리 변환.

## TokenData
OAuth 토큰 데이터. 만료 확인(`is_expired`, `is_refresh_expired`), JSON 직렬화(`to_dict`/`from_dict`).

## Manufacturer
제조사 정보. API 응답에서 `from_dict()`로 생성.

## Category
카테고리 정보. 재귀적 `children` 지원. `from_dict()`로 생성.

## Parameter
부품 파라미터 (parameter_id, name, value).

## PriceBreak
가격 구간 (break_quantity, unit_price, total_price).

## ProductVariation
제품 변형. PriceBreak 리스트 포함. 패키지 타입, 수량, MOQ 정보.

## Product
제품 전체 정보. Manufacturer, Category, Parameter, ProductVariation 중첩 포함.
`from_dict()`에서 Description, ProductStatus 등 복합 필드 처리.

## FilterOptions
검색 필터. `to_dict()`로 PascalCase 변환. None/빈 값 제외.

## SortOptions
정렬 옵션 (field, sort_order). `to_dict()`로 PascalCase 변환.

## KeywordSearchRequest
키워드 검색 요청. FilterOptions, SortOptions 포함 가능. `to_dict()`로 API 요청 본문 생성.

## KeywordSearchResponse
키워드 검색 응답. products, exact_matches, filter_options 포함. `from_dict()`로 파싱.

## ProductPricingResponse
가격 조회 응답. products 리스트와 count. `from_dict()`로 파싱.
