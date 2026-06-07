import httpx
import respx
import pytest

from ff_digikey_api.Core.HttpClient.HttpClient import HttpClient
from ff_digikey_api.Core.HttpClient.ApiError import ApiError
from ff_digikey_api.Core.HttpClient.RateLimitError import RateLimitError
from ff_digikey_api.Structs.DigiKeyLocale import DigiKeyLocale


BASE_URL = "https://api.digikey.com/products/v4"


class TestHttpClientInit:
    def test_stores_base_url(self):
        locale = DigiKeyLocale()
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        assert client._base_url == BASE_URL
        client.close()

    def test_stores_client_id(self):
        locale = DigiKeyLocale()
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        assert client._client_id == "test-id"
        client.close()

    def test_stores_locale(self):
        locale = DigiKeyLocale(language="ko", currency="KRW", site="KR")
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        assert client._locale is locale
        client.close()


class TestHttpClientHeaders:
    def test_build_headers_contains_authorization(self):
        locale = DigiKeyLocale()
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        headers = client._build_headers("my-token")
        assert headers["Authorization"] == "Bearer my-token"
        client.close()

    def test_build_headers_contains_client_id(self):
        locale = DigiKeyLocale()
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        headers = client._build_headers("my-token")
        assert headers["X-DIGIKEY-Client-Id"] == "test-id"
        client.close()

    def test_build_headers_contains_locale(self):
        locale = DigiKeyLocale(language="ko", currency="KRW", site="KR")
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        headers = client._build_headers("my-token")
        assert headers["X-DIGIKEY-Locale-Language"] == "ko"
        assert headers["X-DIGIKEY-Locale-Currency"] == "KRW"
        assert headers["X-DIGIKEY-Locale-Site"] == "KR"
        client.close()


class TestHttpClientGet:
    @respx.mock
    def test_get_success(self):
        locale = DigiKeyLocale()
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        route = respx.get(f"{BASE_URL}/search/keyword").mock(
            return_value=httpx.Response(200, json={"results": []})
        )
        result = client.get("/search/keyword", token="my-token")
        assert result == {"results": []}
        assert route.called
        client.close()

    @respx.mock
    def test_get_with_params(self):
        locale = DigiKeyLocale()
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        route = respx.get(f"{BASE_URL}/search/keyword", params={"q": "resistor"}).mock(
            return_value=httpx.Response(200, json={"results": ["R1"]})
        )
        result = client.get("/search/keyword", token="my-token", params={"q": "resistor"})
        assert result == {"results": ["R1"]}
        client.close()

    @respx.mock
    def test_get_sends_correct_headers(self):
        locale = DigiKeyLocale()
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        route = respx.get(f"{BASE_URL}/search/keyword").mock(
            return_value=httpx.Response(200, json={})
        )
        client.get("/search/keyword", token="my-token")
        request = route.calls[0].request
        assert request.headers["Authorization"] == "Bearer my-token"
        assert request.headers["X-DIGIKEY-Client-Id"] == "test-id"
        client.close()

    @respx.mock
    def test_get_4xx_raises_api_error(self):
        locale = DigiKeyLocale()
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        respx.get(f"{BASE_URL}/search/keyword").mock(
            return_value=httpx.Response(
                404,
                json={"ErrorMessage": "Not Found", "RequestId": "req-001"},
            )
        )
        with pytest.raises(ApiError) as exc_info:
            client.get("/search/keyword", token="my-token")
        assert exc_info.value.status_code == 404
        assert exc_info.value.message == "Not Found"
        assert exc_info.value.request_id == "req-001"
        client.close()

    @respx.mock
    def test_get_5xx_raises_api_error(self):
        locale = DigiKeyLocale()
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        respx.get(f"{BASE_URL}/search/keyword").mock(
            return_value=httpx.Response(
                500,
                json={"ErrorMessage": "Internal Error", "RequestId": "req-002"},
            )
        )
        with pytest.raises(ApiError) as exc_info:
            client.get("/search/keyword", token="my-token")
        assert exc_info.value.status_code == 500
        client.close()

    @respx.mock
    def test_get_429_raises_rate_limit_error(self):
        locale = DigiKeyLocale()
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        respx.get(f"{BASE_URL}/search/keyword").mock(
            return_value=httpx.Response(
                429,
                headers={"Retry-After": "30"},
                json={"ErrorMessage": "Rate limit exceeded", "RequestId": "req-003"},
            )
        )
        with pytest.raises(RateLimitError) as exc_info:
            client.get("/search/keyword", token="my-token")
        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 30
        client.close()

    @respx.mock
    def test_get_429_retries_then_succeeds(self):
        locale = DigiKeyLocale()
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        route = respx.get(f"{BASE_URL}/search/keyword").mock(
            side_effect=[
                httpx.Response(429, headers={"Retry-After": "0"}, json={"ErrorMessage": "Rate limit"}),
                httpx.Response(200, json={"results": ["ok"]}),
            ]
        )
        result = client.get("/search/keyword", token="my-token")
        assert result == {"results": ["ok"]}
        assert route.call_count == 2
        client.close()

    @respx.mock
    def test_get_429_max_retries_exceeded(self):
        locale = DigiKeyLocale()
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        respx.get(f"{BASE_URL}/search/keyword").mock(
            return_value=httpx.Response(
                429,
                headers={"Retry-After": "0"},
                json={"ErrorMessage": "Rate limit exceeded", "RequestId": "req-004"},
            )
        )
        with pytest.raises(RateLimitError):
            client.get("/search/keyword", token="my-token")
        client.close()


class TestHttpClientPost:
    @respx.mock
    def test_post_success(self):
        locale = DigiKeyLocale()
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        route = respx.post(f"{BASE_URL}/search/keyword").mock(
            return_value=httpx.Response(200, json={"results": ["capacitor"]})
        )
        result = client.post("/search/keyword", token="my-token", json_body={"keyword": "cap"})
        assert result == {"results": ["capacitor"]}
        assert route.called
        client.close()

    @respx.mock
    def test_post_sends_correct_headers(self):
        locale = DigiKeyLocale()
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        route = respx.post(f"{BASE_URL}/search/keyword").mock(
            return_value=httpx.Response(200, json={})
        )
        client.post("/search/keyword", token="my-token", json_body={"keyword": "cap"})
        request = route.calls[0].request
        assert request.headers["Authorization"] == "Bearer my-token"
        assert request.headers["X-DIGIKEY-Client-Id"] == "test-id"
        client.close()

    @respx.mock
    def test_post_4xx_raises_api_error(self):
        locale = DigiKeyLocale()
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        respx.post(f"{BASE_URL}/search/keyword").mock(
            return_value=httpx.Response(
                400,
                json={"ErrorMessage": "Bad Request", "RequestId": "req-005"},
            )
        )
        with pytest.raises(ApiError) as exc_info:
            client.post("/search/keyword", token="my-token", json_body={})
        assert exc_info.value.status_code == 400
        client.close()

    @respx.mock
    def test_post_429_retries_then_succeeds(self):
        locale = DigiKeyLocale()
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        route = respx.post(f"{BASE_URL}/search/keyword").mock(
            side_effect=[
                httpx.Response(429, headers={"Retry-After": "0"}, json={"ErrorMessage": "Rate limit"}),
                httpx.Response(200, json={"results": ["ok"]}),
            ]
        )
        result = client.post("/search/keyword", token="my-token", json_body={"keyword": "cap"})
        assert result == {"results": ["ok"]}
        assert route.call_count == 2
        client.close()


class TestHttpClientClose:
    def test_close(self):
        locale = DigiKeyLocale()
        client = HttpClient(base_url=BASE_URL, client_id="test-id", locale=locale)
        client.close()
        assert client._client.is_closed
