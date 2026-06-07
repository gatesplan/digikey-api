# TokenStorage
OAuth 토큰 파일 기반 영속화 모듈. JSON 형식으로 TokenData를 저장/로드.

## TokenStorage
토큰 데이터의 파일 저장소.

### Properties
```python
_file_path: str    # 토큰 저장 파일 경로
```

### __init__
```python
__init__(file_path: str)
    # 파일 경로 설정
```

### Methods

```python
save(token_data: TokenData)
    # token_data.to_dict() -> JSON 파일 저장
```

```python
load() -> TokenData | None
    # 파일 없으면 None 반환
    # JSON 파일 읽기 -> TokenData.from_dict()
```

```python
clear()
    # 파일 삭제 (없으면 무시)
```

```python
exists() -> bool
    # 파일 존재 여부 반환
```
