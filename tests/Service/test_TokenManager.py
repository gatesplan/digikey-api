import time
from unittest.mock import patch, MagicMock

import pytest

from ff_digikey_api.Structs.DigiKeyConfig import DigiKeyConfig
from ff_digikey_api.Structs.TokenData import TokenData
from ff_digikey_api.Service.TokenManager.TokenExpiredError import TokenExpiredError
from ff_digikey_api.Service.TokenManager.TokenManager import TokenManager


# --- TokenExpiredError ---

class TestTokenExpiredError:
    def test_default_message(self):
        err = TokenExpiredError()
        assert "Re-authentication required" in str(err)

    def test_custom_message(self):
        err = TokenExpiredError("Custom error")
        assert str(err) == "Custom error"

    def test_is_exception(self):
        assert issubclass(TokenExpiredError, Exception)


# --- TokenManager 초기화 ---

class TestTokenManagerInit:
    def test_stores_config(self):
        config = DigiKeyConfig(client_id="cid", client_secret="csec")
        tm = TokenManager(config)
        assert tm._config is config

    def test_creates_token_storage(self):
        config = DigiKeyConfig(client_id="cid", client_secret="csec", storage_path="test.json")
        tm = TokenManager(config)
        assert tm._storage._file_path == "test.json"

    def test_cached_token_none_initially(self):
        config = DigiKeyConfig(client_id="cid", client_secret="csec")
        tm = TokenManager(config)
        assert tm._cached_token is None


# --- get_access_token (client_credentials: lazy 발급) ---

class TestGetAccessToken:
    def _make_config(self):
        return DigiKeyConfig(client_id="cid", client_secret="csec")

    def _token(self, access, ttl=3600):
        return TokenData(access_token=access, expires=time.time() + ttl)

    def test_cached_valid_token_returned_immediately(self):
        tm = TokenManager(self._make_config())
        tm._cached_token = self._token("valid-token")
        with patch.object(tm, "_fetch_token") as mock_fetch:
            assert tm.get_access_token() == "valid-token"
            mock_fetch.assert_not_called()

    def test_loads_valid_token_from_storage(self):
        tm = TokenManager(self._make_config())
        with patch.object(tm._storage, "load", return_value=self._token("stored-token")):
            with patch.object(tm, "_fetch_token") as mock_fetch:
                assert tm.get_access_token() == "stored-token"
                mock_fetch.assert_not_called()

    def test_expired_cached_token_fetches_new(self):
        tm = TokenManager(self._make_config())
        tm._cached_token = self._token("expired", ttl=-100)
        new = self._token("fresh-token")
        with patch.object(tm, "_fetch_token", return_value=new) as mock_fetch:
            with patch.object(tm._storage, "save") as mock_save:
                assert tm.get_access_token() == "fresh-token"
                mock_fetch.assert_called_once()
                mock_save.assert_called_once()

    def test_no_token_fetches_new(self):
        tm = TokenManager(self._make_config())
        new = self._token("fresh-token")
        with patch.object(tm._storage, "load", return_value=None):
            with patch.object(tm, "_fetch_token", return_value=new) as mock_fetch:
                with patch.object(tm._storage, "save"):
                    assert tm.get_access_token() == "fresh-token"
                    mock_fetch.assert_called_once()

    def test_expired_stored_token_fetches_new(self):
        tm = TokenManager(self._make_config())
        with patch.object(tm._storage, "load", return_value=self._token("old", ttl=-100)):
            new = self._token("fresh-token")
            with patch.object(tm, "_fetch_token", return_value=new) as mock_fetch:
                with patch.object(tm._storage, "save"):
                    assert tm.get_access_token() == "fresh-token"
                    mock_fetch.assert_called_once()


# --- is_authenticated ---

class TestIsAuthenticated:
    def _make_config(self):
        return DigiKeyConfig(client_id="cid", client_secret="csec")

    def test_no_token_returns_false(self):
        tm = TokenManager(self._make_config())
        with patch.object(tm._storage, "load", return_value=None):
            assert tm.is_authenticated() is False

    def test_valid_token_returns_true(self):
        tm = TokenManager(self._make_config())
        tm._cached_token = TokenData(access_token="at", expires=time.time() + 3600)
        assert tm.is_authenticated() is True

    def test_expired_token_returns_false(self):
        tm = TokenManager(self._make_config())
        tm._cached_token = TokenData(access_token="at", expires=time.time() - 100)
        assert tm.is_authenticated() is False


# --- _get_token_url ---

class TestTokenManagerUrls:
    def test_token_url_production(self):
        tm = TokenManager(DigiKeyConfig(client_id="cid", client_secret="csec", sandbox=False))
        assert "sandbox" not in tm._get_token_url()

    def test_token_url_sandbox(self):
        tm = TokenManager(DigiKeyConfig(client_id="cid", client_secret="csec", sandbox=True))
        assert "sandbox" in tm._get_token_url()


# --- _fetch_token (client_credentials) ---

class TestFetchToken:
    @patch("ff_digikey_api.Service.TokenManager.TokenManager.httpx.post")
    def test_fetch_token_returns_token_data(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new-at",
            "expires_in": 599,
            "token_type": "Bearer",
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        tm = TokenManager(DigiKeyConfig(client_id="cid", client_secret="csec"))
        token = tm._fetch_token()

        assert token.access_token == "new-at"
        assert token.refresh_token is None
        assert token.token_type == "Bearer"
        # 이중 마진 없음: expires는 대략 now + 599
        assert token.expires > time.time() + 500

    @patch("ff_digikey_api.Service.TokenManager.TokenManager.httpx.post")
    def test_fetch_token_sends_client_credentials(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "at", "expires_in": 599}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        tm = TokenManager(DigiKeyConfig(client_id="cid", client_secret="csec"))
        tm._fetch_token()

        call_kwargs = mock_post.call_args
        data = call_kwargs.kwargs.get("data") or call_kwargs[1].get("data")
        assert data["grant_type"] == "client_credentials"
        assert data["client_id"] == "cid"
        assert data["client_secret"] == "csec"
        # 인가코드/리다이렉트 없음
        assert "code" not in data
        assert "redirect_uri" not in data

    @patch("ff_digikey_api.Service.TokenManager.TokenManager.httpx.post")
    def test_fetch_token_invalid_credentials_raises(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        tm = TokenManager(DigiKeyConfig(client_id="bad", client_secret="bad"))
        with pytest.raises(TokenExpiredError):
            tm._fetch_token()

    @patch("ff_digikey_api.Service.TokenManager.TokenManager.httpx.post")
    def test_authorize_fetches_and_saves(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "at", "expires_in": 599}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        tm = TokenManager(DigiKeyConfig(client_id="cid", client_secret="csec"))
        with patch.object(tm._storage, "save") as mock_save:
            tm.authorize()
            mock_save.assert_called_once()
        assert tm._cached_token.access_token == "at"
