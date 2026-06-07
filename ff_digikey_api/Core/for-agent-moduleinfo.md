# Core
인프라 계층. HTTP 통신, 토큰 영속화를 담당. Structs, Constants 의존.

## HttpClient
DigiKey API와의 HTTP 통신 담당. Bearer 인증, Locale 헤더, 429 재시도 로직 포함.
ApiError, RateLimitError 예외 클래스 제공.

## TokenStorage
OAuth 토큰의 파일 기반 영속화(캐시). JSON 형식으로 저장/로드/삭제.
