# -*- coding: utf-8 -*-

from abc import ABC
from collections import defaultdict, OrderedDict
from typing import Dict, Generic, TypeVar, Union

from typing_extensions import Literal

from pyee.errors import PyeeError
from pyee.handlers import ErrorHandlerP, NewListenerHandlerP, UserHandlerP

Event = TypeVar(name="Event")
ErrorEvent = TypeVar(name="ErrorEvent")
NewListenerEvent = Literal["new_listener"]
Arg = TypeVar(name="Arg")
Kwarg = TypeVar(name="Kwarg")
Error = TypeVar(name="Error")


class Entry(ABC, Generic[Event, ErrorEvent, Arg, Kwarg, Error]):
    """
    An abstract table entry.
    """
    def __init__(
        self,
        handler: Union[
            UserHandlerP[Arg, Kwarg],
            ErrorHandlerP[Error],
            NewListenerHandlerP[Event, ErrorEvent, Arg, Kwarg, Error],
        ],
    ):

        self.handler = handler

    def get_handler(
        self,
    ) -> Union[
        UserHandlerP[Arg, Kwarg],
        ErrorHandlerP[Error],
        NewListenerHandlerP[Event, ErrorEvent, Arg, Kwarg, Error],
    ]:
        ...


class UserEntry(Entry[Event, ErrorEvent, Arg, Kwarg, Error]):
    """
    A table entry wrapping a UserHandlerP.
    """
    def __init__(self, handler: UserHandlerP[Arg, Kwarg]):
        self.handler = handler

    def get_handler(self) -> UserHandlerP[Arg, Kwarg]:
        return self.handler


class ErrorEntry(Entry[Event, ErrorEvent, Arg, Kwarg, Error]):
    """
    A table entry wrapping an ErrorHandlerP.
    """
    def __init__(self, handler: ErrorHandlerP[Error]):
        self.handler = handler

    def get_handler(self) -> ErrorHandlerP[Error]:
        return self.handler


class NewListenerEntry(Entry[Event, ErrorEvent, Arg, Kwarg, Error]):
    """
    A table entry wrapping a NewListenerHandlerP.
    """
    def __init__(
        self, handler: NewListenerHandlerP[Event, ErrorEvent, Arg, Kwarg, Error]
    ):
        self.handler = handler

    def get_handler(
        self,
    ) -> NewListenerHandlerP[Event, ErrorEvent, Arg, Kwarg, Error]:
        return self.handler


class Table(Generic[Event, ErrorEvent, Arg, Kwarg, Error]):
    """
    An internal events table.
    """

    def __init__(self):
        self.handlers: Dict[
            Union[Event, ErrorEvent, NewListenerEvent],
            """
            OrderedDict[
                Union[
                    UserHandlerP[Arg, Kwarg],
                    ErrorHandlerP[Error],
                    NewListenerHandlerP[Event, ErrorEvent, Arg, Kwarg, Error]
                ],
                Entry[Event, ErrorEvent, Arg, Kwarg, Error]
            ]
            """,
        ] = defaultdict(OrderedDict)

    def get_user_handler(
        self, event: Event, key: UserHandlerP[Arg, Kwarg]
    ) -> UserHandlerP[Arg, Kwarg]:
        entry: Entry[Event, ErrorEvent, Arg, Kwarg, Error] = self.handlers[event][
            key
        ]
        if isinstance(entry, UserEntry):
            return entry.get_handler()

        raise PyeeError(f"Unexpected handler: {entry.get_handler()}")

    def get_error_handler(
        self, event: ErrorEvent, key: ErrorHandlerP[Error]
    ) -> ErrorHandlerP[Error]:
        entry: Entry[Event, ErrorEvent, Arg, Kwarg, Error] = self.handlers[event][
            key
        ]
        if isinstance(entry, ErrorEntry):
            return entry.get_handler()
        raise PyeeError(f"Unexpected handler: {entry.get_handler()}")

    def get_new_listener_handler(
        self, key: NewListenerHandlerP[Event, ErrorEvent, Arg, Kwarg, Error]
    ) -> NewListenerHandlerP[Event, ErrorEvent, Arg, Kwarg, Error]:
        entry: Entry[Event, ErrorEvent, Arg, Kwarg, Error] = self.handlers[
            "new_listener"
        ][key]
        if isinstance(entry, NewListenerEntry):
            return entry.get_handler()
        raise PyeeError(f"Unexpected handler: {entry.get_handler()}")
