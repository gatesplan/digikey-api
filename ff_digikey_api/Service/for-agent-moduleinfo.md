# Service
비즈니스 로직 처리 서비스 계층. Structs, Core, Constants 모듈 의존.

## TokenManager
OAuth 2.0 토큰 관리. 최초 인증, 토큰 갱신, 캐싱, 저장 담당.
TokenExpiredError 예외로 재인증 필요 상태 통보.

## ProductService
DigiKey Products V4 API 호출 래퍼. HttpClient를 통해 검색, 상세, 가격, 연관/대체, 참조 데이터 조회.
