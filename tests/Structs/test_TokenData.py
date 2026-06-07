import time

from ff_digikey_api.Structs.TokenData import TokenData


class TestTokenData:
    def test_is_expired_when_expired(self):
        token = TokenData(access_token="abc", expires=time.time() - 100)
        assert token.is_expired() is True

    def test_is_expired_when_valid(self):
        token = TokenData(access_token="abc", expires=time.time() + 3600)
        assert token.is_expired() is False

    def test_is_expired_with_margin(self):
        # 현재 + 20초 후 만료, margin=30이면 만료로 판정
        token = TokenData(access_token="abc", expires=time.time() + 20)
        assert token.is_expired(margin=30.0) is True

    def test_is_expired_with_margin_valid(self):
        # 현재 + 60초 후 만료, margin=30이면 유효
        token = TokenData(access_token="abc", expires=time.time() + 60)
        assert token.is_expired(margin=30.0) is False

    def test_is_refresh_expired_no_refresh_token(self):
        token = TokenData(access_token="abc")
        assert token.is_refresh_expired() is True

    def test_is_refresh_expired_when_expired(self):
        token = TokenData(
            access_token="abc",
            refresh_token="ref",
            refresh_token_expires=time.time() - 100,
        )
        assert token.is_refresh_expired() is True

    def test_is_refresh_expired_when_valid(self):
        token = TokenData(
            access_token="abc",
            refresh_token="ref",
            refresh_token_expires=time.time() + 3600,
        )
        assert token.is_refresh_expired() is False

    def test_to_dict_from_dict_roundtrip(self):
        original = TokenData(
            access_token="abc123",
            refresh_token="ref456",
            expires=1700000000.0,
            refresh_token_expires=1700100000.0,
            token_type="Bearer",
        )
        data = original.to_dict()
        restored = TokenData.from_dict(data)
        assert restored.access_token == original.access_token
        assert restored.refresh_token == original.refresh_token
        assert restored.expires == original.expires
        assert restored.refresh_token_expires == original.refresh_token_expires
        assert restored.token_type == original.token_type

    def test_to_dict_keys(self):
        token = TokenData(access_token="abc")
        d = token.to_dict()
        assert "access_token" in d
        assert "refresh_token" in d
        assert "expires" in d
        assert "refresh_token_expires" in d
        assert "token_type" in d
