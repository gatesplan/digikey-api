# DigiKeyClient
DigiKey API v4 통합 클라이언트. TokenManager와 ProductService를 조합하여 사용자에게 단일 인터페이스 제공.

## DigiKeyClient
최상위 API 클라이언트. context manager 지원.

### Properties
```python
_config: DigiKeyConfig             # API 설정
_locale: DigiKeyLocale             # 로케일 설정
_token_manager: TokenManager       # 토큰 관리자
_http_client: HttpClient           # HTTP 클라이언트
_product_service: ProductService   # 제품 서비스
```

### __init__
```python
__init__(client_id: str, client_secret: str, locale: DigiKeyLocale | None = None, **kwargs)
    # kwargs: sandbox, storage_path
    # 내부 컴포넌트(TokenManager, HttpClient, ProductService) 자동 생성
```

### Methods

```python
@classmethod
from_env(env_file: str | None = None) -> DigiKeyClient
    raise ValueError
    # 환경변수에서 설정 로드하여 인스턴스 생성
    # DIGIKEY_CLIENT_ID, DIGIKEY_CLIENT_SECRET 필수
    # DIGIKEY_LANGUAGE, DIGIKEY_CURRENCY, DIGIKEY_SITE, DIGIKEY_SANDBOX 선택
```

```python
authorize()
    # client_credentials 토큰 발급 (브라우저 없음, 선택적; TokenManager 위임)
```

```python
search(keywords: str, limit: int = 10, offset: int = 0, filters: FilterOptions | None = None, sort: SortOptions | None = None) -> KeywordSearchResponse
    # 키워드 검색, 토큰 자동 획득. limit는 1~50으로 클램프.
```

```python
detect_leaf_category(keywords: str, filters: FilterOptions | None = None) -> int | None
    # 검색 결과 첫 제품의 카테고리에서 리프 카테고리 ID 추출 (없으면 None)
```

```python
parametric_search(keywords, expressions, limit=10, offset=0, filters=None, sort=None, category_id=None) -> KeywordSearchResponse
    raise ValueError   # 카테고리/ParametricFilters 미발견 시
    # 표현식 기반 파라미터 필터 검색. category_id 미지정시 detect_leaf_category로 자동 감지.
```

```python
product_details(product_number: str) -> Product
    # 제품 상세 조회
```

```python
pricing(product_number: str, **kwargs) -> ProductPricingResponse
    # 가격 조회
```

```python
associations(product_number: str) -> list[Product]
    # 연관 제품 조회
```

```python
substitutions(product_number: str) -> list[Product]
    # 대체 제품 조회
```

```python
recommended_products(product_number: str) -> list[Product]
    # 추천 제품 조회
```

```python
alternate_packaging(product_number: str) -> list[Product]
    # 대체 패키징 조회
```

```python
media(product_number: str) -> dict
    # 미디어 링크 조회
```

```python
manufacturers() -> list[Manufacturer]
    # 제조사 목록 조회
```

```python
categories() -> list[Category]
    # 카테고리 목록 조회
```

```python
close()
    # HttpClient 종료
```
