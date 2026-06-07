from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class TokenData:
    access_token: str
    refresh_token: str | None = None
    expires: float = 0.0
    refresh_token_expires: float | None = None
    token_type: str = "Bearer"

    def is_expired(self, margin: float = 30.0) -> bool:
        # 현재 시간 + margin 이후에 만료되면 True
        return time.time() + margin >= self.expires

    def is_refresh_expired(self) -> bool:
        # refresh_token이 없거나 만료되면 True
        if self.refresh_token is None:
            return True
        if self.refresh_token_expires is None:
            return True
        return time.time() >= self.refresh_token_expires

    def to_dict(self) -> dict:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires": self.expires,
            "refresh_token_expires": self.refresh_token_expires,
            "token_type": self.token_type,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TokenData":
        return cls(
            access_token=data.get("access_token", ""),
            refresh_token=data.get("refresh_token"),
            expires=data.get("expires", 0.0),
            refresh_token_expires=data.get("refresh_token_expires"),
            token_type=data.get("token_type", "Bearer"),
        )
