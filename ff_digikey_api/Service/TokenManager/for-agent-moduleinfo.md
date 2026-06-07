# TokenManager
OAuth 2.0 토큰 생명주기 관리. DigiKeyConfig 기반 초기화.

## TokenExpiredError
자격증명 무효 등으로 토큰 발급이 불가능할 때 발생하는 예외.

## TokenManager
2-Legged OAuth(client_credentials) 인증 흐름, 토큰 캐싱, 만료시 자동 재발급.
브라우저/콜백 서버/refresh 토큰을 사용하지 않는다.

### Properties
```python
_config: DigiKeyConfig            # API 설정
_storage: TokenStorage            # 토큰 파일 저장소(캐시)
_cached_token: TokenData | None   # 메모리 캐싱된 토큰
```

### __init__
```python
__init__(config: DigiKeyConfig)
    # DigiKeyConfig로 TokenStorage 생성
```

### Methods

```python
authorize()
    # client_credentials로 토큰 발급/저장 (브라우저 없음).
    # get_access_token이 lazy 발급하므로 호출은 선택적(자격증명 사전검증 용도).
```

```python
get_access_token() -> str
    raise TokenExpiredError   # 자격증명 무효(400/401) 시
    # 유효한 access_token 반환.
    # 캐시 유효 -> 반환 / 캐시없음 -> 저장소 로드 / 없거나 만료 -> 재발급(_fetch_token)
```

```python
is_authenticated() -> bool
    # 캐시/저장 토큰이 존재하고 만료되지 않았는지 확인.
    # 만료/없음이어도 자격증명만 있으면 get_access_token이 자동 발급한다.
```

```python
_fetch_token() -> TokenData
    raise TokenExpiredError   # 400/401(자격증명 무효)
    # grant_type=client_credentials로 TOKEN_URL에 POST하여 토큰 발급.
    # refresh_token은 None. expires = now + expires_in (만료 마진은 is_expired가 처리).
```

```python
_get_token_url() -> str
    # sandbox 여부에 따라 TOKEN_URL 반환
```
