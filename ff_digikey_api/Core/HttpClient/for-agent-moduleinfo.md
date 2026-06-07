# HttpClient
DigiKey Products V4 API HTTP 통신 모듈. httpx 기반 동기 클라이언트.

## ApiError
API 오류 응답을 나타내는 예외 클래스.

### Properties
```python
status_code: int    # HTTP 상태 코드
message: str        # 오류 메시지
request_id: str     # DigiKey 요청 ID
```

### __init__
```python
__init__(status_code: int, message: str, request_id: str = "")
    # str(error) 포맷: "[{status_code}] {message}"
```

## RateLimitError
429 응답 전용 예외. ApiError 상속.

### Properties
```python
retry_after: int | None    # Retry-After 헤더 값 (초)
```

### __init__
```python
__init__(message: str = "Rate limit exceeded", request_id: str = "", retry_after: int | None = None)
    # status_code는 항상 429
```

## HttpClient
DigiKey API 동기 HTTP 클라이언트.

### Properties
```python
_base_url: str              # API 기본 URL
_client_id: str             # DigiKey Client ID
_locale: DigiKeyLocale      # 로케일 설정
_client: httpx.Client       # httpx 동기 클라이언트 (timeout=30s)
```

### __init__
```python
__init__(base_url: str, client_id: str, locale: DigiKeyLocale)
    # httpx.Client 생성, 기본 타임아웃 30초
```

### Methods

```python
get(path: str, token: str, params: dict | None = None) -> dict
    raise ApiError
    raise RateLimitError
    # GET 요청 수행, Authorization/Locale/Client-Id 헤더 자동 추가
    # 429 발생 시 Retry-After 파싱하여 재시도 (최대 3회)
    # 4xx/5xx 시 ApiError 발생
```

```python
post(path: str, token: str, json_body: dict) -> dict
    raise ApiError
    raise RateLimitError
    # POST 요청 수행, get과 동일 패턴
```

```python
_build_headers(token: str) -> dict
    # Bearer + Locale + Client-Id 헤더 조합
```

```python
_handle_error(response: httpx.Response)
    raise ApiError
    raise RateLimitError
    # 429 -> RateLimitError, 그 외 -> ApiError
    # 응답 body에서 ErrorMessage, RequestId 추출
```

```python
close()
    # httpx.Client 종료
```
