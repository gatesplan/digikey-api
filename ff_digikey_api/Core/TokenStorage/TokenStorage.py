import json
import os

from loguru import logger

from ff_digikey_api.Structs.TokenData import TokenData


class TokenStorage:
    def __init__(self, file_path: str):
        self._file_path = file_path
        logger.info(f"TokenStorage 초기화: file_path={file_path}")

    def save(self, token_data: TokenData):
        logger.info("토큰 저장 시작")
        with open(self._file_path, "w") as f:
            json.dump(token_data.to_dict(), f)
        logger.info("토큰 저장 완료")

    def load(self) -> TokenData | None:
        logger.info("토큰 로드 시작")
        if not os.path.exists(self._file_path):
            logger.info("토큰 파일 없음")
            return None
        with open(self._file_path, "r") as f:
            data = json.load(f)
        return TokenData.from_dict(data)

    def clear(self):
        logger.info("토큰 삭제 시작")
        if os.path.exists(self._file_path):
            os.remove(self._file_path)
            logger.info("토큰 파일 삭제 완료")

    def exists(self) -> bool:
        return os.path.exists(self._file_path)
