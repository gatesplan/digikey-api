import time

import httpx
from loguru import logger

from ff_digikey_api.Constants.Endpoints import TOKEN_URL, SANDBOX_TOKEN_URL
from ff_digikey_api.Structs.DigiKeyConfig import DigiKeyConfig
from ff_digikey_api.Structs.TokenData import TokenData
from ff_digikey_api.Core.TokenStorage.TokenStorage import TokenStorage
from ff_digikey_api.Service.TokenManager.TokenExpiredError import TokenExpiredError


class TokenManager:
    def __init__(self, config: DigiKeyConfig):
        self._config = config
        self._storage = TokenStorage(config.storage_path)
        self._cached_token: TokenData | None = None
        logger.info("TokenManager 초기화")

    def authorize(self):
        # 2-legged(client_credentials): 브라우저/콜백 없이 토큰만 발급/저장.
        # get_access_token이 lazy 발급하므로 호출은 선택적(자격증명 사전검증 용도).
        logger.info("authorize 시작 (client_credentials)")
        self._cached_token = self._fetch_token()
        self._storage.save(self._cached_token)
        logger.info("authorize 완료")

    def get_access_token(self) -> str:
        logger.info("get_access_token 시작")
        # 1. 캐시된 토큰이 유효하면 즉시 반환
        if self._cached_token and not self._cached_token.is_expired():
            return self._cached_token.access_token

        # 2. 캐시 없으면 저장소에서 로드
        if self._cached_token is None:
            self._cached_token = self._storage.load()

        # 3. 토큰이 없거나 만료 -> 새로 발급 (client_credentials는 refresh 불필요)
        if self._cached_token is None or self._cached_token.is_expired():
            self._cached_token = self._fetch_token()
            self._storage.save(self._cached_token)

        return self._cached_token.access_token

    def is_authenticated(self) -> bool:
        logger.info("is_authenticated 확인")
        # 유효한 캐시/저장 토큰이 있으면 True.
        # 없거나 만료여도 자격증명만 있으면 get_access_token이 자동 발급한다.
        token = self._cached_token
        if token is None:
            token = self._storage.load()
        return token is not None and not token.is_expired()

    def _fetch_token(self) -> TokenData:
        logger.info("_fetch_token 시작 (client_credentials)")
        url = self._get_token_url()
        data = {
            "grant_type": "client_credentials",
            "client_id": self._config.client_id,
            "client_secret": self._config.client_secret,
        }
        response = httpx.post(url, data=data)
        if response.status_code in (400, 401):
            logger.error(f"토큰 발급 실패 ({response.status_code}): 자격증명 확인 필요")
            raise TokenExpiredError(
                "Invalid client credentials. Check DIGIKEY_CLIENT_ID/DIGIKEY_CLIENT_SECRET."
            )
        response.raise_for_status()
        body = response.json()
        now = time.time()
        expires_in = body.get("expires_in", 0)
        # 만료 마진은 TokenData.is_expired(margin)가 단독 처리한다 (여기서 -30 하지 않음).
        return TokenData(
            access_token=body["access_token"],
            refresh_token=None,
            expires=now + expires_in,
            refresh_token_expires=None,
            token_type=body.get("token_type", "Bearer"),
        )

    def _get_token_url(self) -> str:
        if self._config.sandbox:
            return SANDBOX_TOKEN_URL
        return TOKEN_URL
