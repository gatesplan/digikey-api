import os
from unittest.mock import patch, MagicMock

import pytest

from ff_digikey_api.API.DigiKeyClient.DigiKeyClient import DigiKeyClient
from ff_digikey_api.Structs.DigiKeyLocale import DigiKeyLocale
from ff_digikey_api.Structs.DigiKeyConfig import DigiKeyConfig
from ff_digikey_api.Structs.KeywordSearchRequest import KeywordSearchRequest
from ff_digikey_api.Structs.KeywordSearchResponse import KeywordSearchResponse
from ff_digikey_api.Structs.Product import Product
from ff_digikey_api.Structs.Manufacturer import Manufacturer
from ff_digikey_api.Structs.Category import Category


class TestDigiKeyClientInit:
    def test_stores_config(self):
        client = DigiKeyClient(client_id="cid", client_secret="csec")
        assert client._config.client_id == "cid"
        assert client._config.client_secret == "csec"
        client.close()

    def test_default_locale(self):
        client = DigiKeyClient(client_id="cid", client_secret="csec")
        assert client._locale.language == "en"
        assert client._locale.currency == "USD"
        client.close()

    def test_custom_locale(self):
        locale = DigiKeyLocale(language="ko", currency="KRW", site="KR")
        client = DigiKeyClient(client_id="cid", client_secret="csec", locale=locale)
        assert client._locale.language == "ko"
        client.close()

    def test_sandbox_mode(self):
        client = DigiKeyClient(client_id="cid", client_secret="csec", sandbox=True)
        assert client._config.sandbox is True
        assert "sandbox" in client._http_client._base_url
        client.close()

    def test_production_mode(self):
        client = DigiKeyClient(client_id="cid", client_secret="csec", sandbox=False)
        assert client._config.sandbox is False
        assert "sandbox" not in client._http_client._base_url
        client.close()

    def test_creates_token_manager(self):
        client = DigiKeyClient(client_id="cid", client_secret="csec")
        assert client._token_manager is not None
        client.close()

    def test_creates_product_service(self):
        client = DigiKeyClient(client_id="cid", client_secret="csec")
        assert client._product_service is not None
        client.close()


class TestFromEnv:
    def test_from_env_reads_environment(self):
        env_vars = {
            "DIGIKEY_CLIENT_ID": "env-cid",
            "DIGIKEY_CLIENT_SECRET": "env-csec",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            client = DigiKeyClient.from_env()
            assert client._config.client_id == "env-cid"
            assert client._config.client_secret == "env-csec"
            client.close()

    def test_from_env_reads_locale(self):
        env_vars = {
            "DIGIKEY_CLIENT_ID": "cid",
            "DIGIKEY_CLIENT_SECRET": "csec",
            "DIGIKEY_LANGUAGE": "ko",
            "DIGIKEY_CURRENCY": "KRW",
            "DIGIKEY_SITE": "KR",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            client = DigiKeyClient.from_env()
            assert client._locale.language == "ko"
            assert client._locale.currency == "KRW"
            assert client._locale.site == "KR"
            client.close()

    def test_from_env_sandbox(self):
        env_vars = {
            "DIGIKEY_CLIENT_ID": "cid",
            "DIGIKEY_CLIENT_SECRET": "csec",
            "DIGIKEY_SANDBOX": "true",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            client = DigiKeyClient.from_env()
            assert client._config.sandbox is True
            client.close()

    def test_from_env_missing_client_id_raises(self):
        env_vars = {"DIGIKEY_CLIENT_SECRET": "csec"}
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError):
                DigiKeyClient.from_env()


class TestSearch:
    def test_search_delegates_to_service(self):
        client = DigiKeyClient(client_id="cid", client_secret="csec")
        mock_response = KeywordSearchResponse(products=[], products_count=0)
        with patch.object(client._token_manager, "get_access_token", return_value="token"):
            with patch.object(client._product_service, "keyword_search", return_value=mock_response) as mock_search:
                result = client.search("STM32", limit=10)
                assert result is mock_response
                mock_search.assert_called_once()
                call_args = mock_search.call_args
                assert call_args[0][0] == "token"
                req = call_args[0][1]
                assert isinstance(req, KeywordSearchRequest)
                assert req.keywords == "STM32"
                assert req.limit == 10
        client.close()


class TestProductDetails:
    def test_product_details_delegates(self):
        client = DigiKeyClient(client_id="cid", client_secret="csec")
        mock_product = MagicMock(spec=Product)
        with patch.object(client._token_manager, "get_access_token", return_value="token"):
            with patch.object(client._product_service, "product_details", return_value=mock_product) as mock_pd:
                result = client.product_details("STM32F407")
                assert result is mock_product
                mock_pd.assert_called_once_with("token", "STM32F407")
        client.close()


class TestSearchLimitClamp:
    def _run(self, limit):
        client = DigiKeyClient(client_id="cid", client_secret="csec")
        mock_response = KeywordSearchResponse(products=[], products_count=0)
        with patch.object(client._token_manager, "get_access_token", return_value="t"):
            with patch.object(client._product_service, "keyword_search", return_value=mock_response) as mock_ks:
                client.search("x", limit=limit)
                req = mock_ks.call_args[0][1]
        client.close()
        return req.limit

    def test_limit_clamped_to_max_50(self):
        assert self._run(200) == 50

    def test_limit_floored_to_1(self):
        assert self._run(0) == 1

    def test_limit_within_range_unchanged(self):
        assert self._run(25) == 25


class TestFindLeafCategory:
    def test_recurses_to_real_leaf(self):
        cat = Category.from_dict({
            "CategoryId": 1, "Name": "Capacitors",
            "ChildCategories": [
                {"CategoryId": 60, "Name": "Ceramic", "ChildCategories": [
                    {"CategoryId": 60131, "Name": "MLCC", "ChildCategories": []},
                ]},
            ],
        })
        assert DigiKeyClient._find_leaf_category(cat) == 60131

    def test_returns_id_when_no_children(self):
        cat = Category.from_dict({"CategoryId": 52, "Name": "Leaf", "ChildCategories": []})
        assert DigiKeyClient._find_leaf_category(cat) == 52


class TestContextManager:
    def test_enter_returns_self(self):
        client = DigiKeyClient(client_id="cid", client_secret="csec")
        assert client.__enter__() is client
        client.close()

    def test_exit_closes_client(self):
        client = DigiKeyClient(client_id="cid", client_secret="csec")
        with patch.object(client, "close") as mock_close:
            client.__exit__(None, None, None)
            mock_close.assert_called_once()

    def test_with_statement(self):
        with DigiKeyClient(client_id="cid", client_secret="csec") as client:
            assert client is not None
        assert client._http_client._client.is_closed
