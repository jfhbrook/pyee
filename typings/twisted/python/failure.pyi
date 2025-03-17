from typing import Any


class Failure(BaseException):
    value: Exception

    def raiseException(self: Any) -> None:
        ...
