from ff_digikey_api.Core.HttpClient.ApiError import ApiError
from ff_digikey_api.Core.HttpClient.RateLimitError import RateLimitError


class TestRateLimitError:
    def test_inherits_api_error(self):
        error = RateLimitError()
        assert isinstance(error, ApiError)

    def test_status_code_is_429(self):
        error = RateLimitError()
        assert error.status_code == 429

    def test_default_message(self):
        error = RateLimitError()
        assert error.message == "Rate limit exceeded"

    def test_custom_message(self):
        error = RateLimitError(message="Too many requests")
        assert error.message == "Too many requests"

    def test_request_id(self):
        error = RateLimitError(request_id="req-456")
        assert error.request_id == "req-456"

    def test_retry_after_default(self):
        error = RateLimitError()
        assert error.retry_after is None

    def test_retry_after_custom(self):
        error = RateLimitError(retry_after=60)
        assert error.retry_after == 60

    def test_str_format(self):
        error = RateLimitError()
        assert str(error) == "[429] Rate limit exceeded"
