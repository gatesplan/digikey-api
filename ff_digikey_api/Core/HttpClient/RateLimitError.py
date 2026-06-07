from ff_digikey_api.Core.HttpClient.ApiError import ApiError


# ApiError를 상속
class RateLimitError(ApiError):
    def __init__(self, message: str = "Rate limit exceeded", request_id: str = "", retry_after: int | None = None):
        self.retry_after = retry_after
        super().__init__(status_code=429, message=message, request_id=request_id)
