# ProductService
DigiKey Products V4 API 엔드포인트 호출 래퍼. HttpClient 의존.

## ProductService
모든 제품 API 호출을 담당. 검색, 상세, 가격, 연관/대체, 참조 데이터 조회.

### Properties
```python
_http_client: HttpClient    # HTTP 요청 클라이언트
```

### __init__
```python
__init__(http_client: HttpClient)
    # HttpClient 인스턴스 저장
```

### Methods

```python
keyword_search(token: str, request: KeywordSearchRequest) -> KeywordSearchResponse
    # POST 키워드 검색
```

```python
product_details(token: str, product_number: str) -> Product
    # GET 제품 상세 조회
```

```python
pricing(token: str, product_number: str, **kwargs) -> ProductPricingResponse
    # GET 가격 조회, kwargs는 쿼리 파라미터
```

```python
associations(token: str, product_number: str) -> list[Product]
    # GET 연관 제품 조회
```

```python
substitutions(token: str, product_number: str) -> list[Product]
    # GET 대체 제품 조회
```

```python
recommended_products(token: str, product_number: str) -> list[Product]
    # GET 추천 제품 조회
```

```python
alternate_packaging(token: str, product_number: str) -> list[Product]
    # GET 대체 패키징 조회
```

```python
media(token: str, product_number: str) -> dict
    # GET 미디어 링크 조회, raw dict 반환
```

```python
digireel_pricing(token: str, product_number: str, requested_quantity: int = 1) -> dict
    # GET DigiReel 가격 조회, raw dict 반환
```

```python
pricing_options_by_quantity(token: str, product_number: str) -> dict
    # GET 수량별 가격 옵션 조회, raw dict 반환
```

```python
manufacturers(token: str) -> list[Manufacturer]
    # GET 제조사 목록 조회
```

```python
categories(token: str) -> list[Category]
    # GET 카테고리 목록 조회
```

```python
category(token: str, category_id: int) -> Category
    # GET 단일 카테고리 조회
```
