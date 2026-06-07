class TokenExpiredError(Exception):
    def __init__(self, message: str = "Token expired and refresh failed. Re-authentication required."):
        super().__init__(message)
