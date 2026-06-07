class ApiError(Exception):
    def __init__(self, status_code: int, message: str, request_id: str = ""):
        self.status_code = status_code
        self.message = message
        self.request_id = request_id
        super().__init__(f"[{status_code}] {message}")
