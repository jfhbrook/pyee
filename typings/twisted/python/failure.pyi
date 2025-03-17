from typing import Self


class Failure(BaseException):
    value: Exception

    def raiseException(self: Self) -> None:
        ...
