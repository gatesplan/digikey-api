import time

import httpx
from loguru import logger

from ff_digikey_api.Constants.Headers import CLIENT_ID
from ff_digikey_api.Structs.DigiKeyLocale import DigiKeyLocale
from ff_digikey_api.Core.HttpClient.ApiError import ApiError
from ff_digikey_api.Core.HttpClient.RateLimitError import RateLimitError


class HttpClient:
    # 429 재시도 최대 횟수
    _MAX_RETRIES = 3

    def __init__(self, base_url: str, client_id: str, locale: DigiKeyLocale):
        self._base_url = base_url
        self._client_id = client_id
        self._locale = locale
        self._client = httpx.Client(base_url=base_url, timeout=30.0)
        logger.info(f"HttpClient 초기화: base_url={base_url}")

    def get(self, path: str, token: str, params: dict | None = None) -> dict:
        logger.info(f"GET 요청 시작: path={path}")
        headers = self._build_headers(token)
        for attempt in range(self._MAX_RETRIES):
            response = self._client.get(path, headers=headers, params=params)
            if response.status_code == 429:
                retry_after = self._parse_retry_after(response)
                logger.debug(f"429 응답, 재시도 {attempt + 1}/{self._MAX_RETRIES}, retry_after={retry_after}")
                if attempt < self._MAX_RETRIES - 1:
                    time.sleep(retry_after)
                    continue
                self._handle_error(response)
            elif response.status_code >= 400:
                self._handle_error(response)
            return response.json()
        # 도달 불가능하지만 안전장치
        self._handle_error(response)

    def post(self, path: str, token: str, json_body: dict) -> dict:
        logger.info(f"POST 요청 시작: path={path}")
        headers = self._build_headers(token)
        for attempt in range(self._MAX_RETRIES):
            response = self._client.post(path, headers=headers, json=json_body)
            if response.status_code == 429:
                retry_after = self._parse_retry_after(response)
                logger.debug(f"429 응답, 재시도 {attempt + 1}/{self._MAX_RETRIES}, retry_after={retry_after}")
                if attempt < self._MAX_RETRIES - 1:
                    time.sleep(retry_after)
                    continue
                self._handle_error(response)
            elif response.status_code >= 400:
                self._handle_error(response)
            return response.json()
        self._handle_error(response)

    def _build_headers(self, token: str) -> dict:
        headers = {
            "Authorization": f"Bearer {token}",
            CLIENT_ID: self._client_id,
        }
        headers.update(self._locale.to_headers())
        return headers

    def _handle_error(self, response: httpx.Response):
        # 응답 body에서 ErrorMessage, RequestId 추출
        try:
            body = response.json()
        except Exception:
            body = {}
        message = body.get("ErrorMessage", response.reason_phrase or "Unknown error")
        request_id = body.get("RequestId", "")

        if response.status_code == 429:
            retry_after = self._parse_retry_after(response)
            raise RateLimitError(
                message=message,
                request_id=request_id,
                retry_after=retry_after,
            )
        raise ApiError(
            status_code=response.status_code,
            message=message,
            request_id=request_id,
        )

    def _parse_retry_after(self, response: httpx.Response) -> int:
        # Retry-After 헤더 파싱
        retry_after_str = response.headers.get("Retry-After")
        if retry_after_str is not None:
            try:
                return int(retry_after_str)
            except ValueError:
                pass
        return 1

    def close(self):
        logger.info("HttpClient 종료")
        self._client.close()
