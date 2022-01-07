# -*- coding: utf-8 -*-

from typing import Any, TypeVar, Union

from typing_extensions import Literal, Protocol

Event = TypeVar(name="Event")
ErrorEvent = TypeVar(name="ErrorEvent")
NewListenerEvent = Literal["new_listener"]

Arg = TypeVar(name="Arg", contravariant=True)
Kwarg = TypeVar(name="Kwarg", contravariant=True)
Error = TypeVar(name="Error", contravariant=True)


class UserHandlerP(Protocol[Arg, Kwarg]):
    """
    A user handler function.
    """

    def __call__(
        self,
        *args: Arg,
        **kwargs: Kwarg,
    ) -> Any:
        ...


class ErrorHandlerP(Protocol[Error]):
    def __call__(self, err: Error) -> Any:
        ...


NLError = TypeVar(name="NLError", covariant=True)
NLArg = TypeVar(name="NLArg", covariant=True)
NLKwarg = TypeVar(name="NLKwarg", covariant=True)
NLEvent = TypeVar(name="NLEvent", contravariant=True)
NLErrorEvent = TypeVar(name="NLErrorEvent", contravariant=True)


class NewListenerHandlerP(Protocol[NLEvent, NLErrorEvent, NLArg, NLKwarg, NLError]):
    def __call__(
        self,
        event: Union[NLEvent, NLErrorEvent],
        handler: Union[UserHandlerP[NLArg, NLKwarg], ErrorHandlerP[NLError]],
    ) -> Any:
        ...
