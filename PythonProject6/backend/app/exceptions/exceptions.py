class AppError(Exception):
    def __init__(self, message: str = "Application error"):
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    pass


class DuplicateError(AppError):
    pass
