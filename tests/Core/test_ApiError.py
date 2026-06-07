from ff_digikey_api.Core.HttpClient.ApiError import ApiError


class TestApiError:
    def test_status_code(self):
        error = ApiError(status_code=400, message="Bad Request")
        assert error.status_code == 400

    def test_message(self):
        error = ApiError(status_code=404, message="Not Found")
        assert error.message == "Not Found"

    def test_request_id_default(self):
        error = ApiError(status_code=500, message="Server Error")
        assert error.request_id == ""

    def test_request_id_custom(self):
        error = ApiError(status_code=500, message="Server Error", request_id="req-123")
        assert error.request_id == "req-123"

    def test_str_format(self):
        error = ApiError(status_code=400, message="Bad Request")
        assert str(error) == "[400] Bad Request"

    def test_is_exception(self):
        error = ApiError(status_code=400, message="Bad Request")
        assert isinstance(error, Exception)
