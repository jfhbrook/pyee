class Failure(BaseException):
    value: Exception

    def raiseException() -> None:
        ...
