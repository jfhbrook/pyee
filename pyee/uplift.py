# -*- coding: utf-8 -*-

from functools import wraps
from typing import Any, Callable, Dict, Optional, Protocol, Tuple, Union

from typing_extensions import Literal

from pyee.base import (
    AnyHandlerP,
    Arg,
    Event,
    EventEmitterP,
    IArg,
    IEvent,
    IKwarg,
    InternalEvent,
    Kwarg,
)

UnwrapMethod = Callable[[], None]


class UpliftedEventEmitterP(EventEmitterP[Event, Arg, Kwarg]):
    @property
    def unwrap(self) -> Optional[UnwrapMethod]:
        ...

    @unwrap.setter
    def unwrap(self, unwrap: UnwrapMethod) -> None:
        ...

    @unwrap.deleter
    def unwrap(self) -> None:
        ...

    def _call_handlers(
        self,
        event: Union[Event, InternalEvent],
        args: Tuple[
            Union[Arg, Exception, Event, InternalEvent, AnyHandlerP],
            ...,
        ],
        kwargs: Dict[str, Kwarg],
    ) -> bool:
        ...

    def _emit_handle_potential_error(
        self,
        event: Union[Event, InternalEvent],
        error: Optional[Union[Arg, Exception, Event, InternalEvent, AnyHandlerP]],
    ) -> None:
        ...


ErrorHandler = Any
ErrorStrategy = str


def _wrap(
    left: UpliftedEventEmitterP[Event, Arg, Kwarg],
    right: UpliftedEventEmitterP[Event, Arg, Kwarg],
    error_handler: UpliftedEventEmitterP,
    proxy_new_listener: bool,
) -> None:
    left_emit = left.emit
    left_unwrap = getattr(left, "unwrap", None)

    @wraps(left_emit)
    def wrapped_emit(
        event: Union[Event, InternalEvent],
        *args: Union[Arg, Exception, Event, InternalEvent, AnyHandlerP],
        **kwargs: Kwarg
    ) -> bool:
        left_handled: bool = left._call_handlers(event, args, kwargs)

        # Do it for the right side
        if proxy_new_listener or event != "new_listener":
            right_handled = right._call_handlers(event, args, kwargs)
        else:
            right_handled = False

        handled = left_handled or right_handled

        # Use the error handling on ``error_handler`` (should either be
        # ``left`` or ``right``)
        if not handled:
            error_handler._emit_handle_potential_error(event, args[0] if args else None)

        return handled

    def unwrap() -> None:
        left.emit = left_emit
        if left_unwrap:
            left.unwrap = left_unwrap
        else:
            del left.unwrap
        left.emit = left_emit

        right_unwrap: Optional[UnwrapMethod] = getattr(right, "unwrap", None)
        if right_unwrap:
            right_unwrap()

    left.emit = wrapped_emit
    left.unwrap = unwrap


_PROXY_NEW_LISTENER_SETTINGS: Dict[str, Tuple[bool, bool]] = dict(
    forward=(False, True),
    backward=(True, False),
    both=(True, True),
    neither=(False, False),
)


class UpliftableEventEmitterFactoryP(Protocol[Event, Arg, Kwarg]):
    def __call__(
        self, *args: Any, **kwargs: Any
    ) -> UpliftedEventEmitterP[Event, Arg, Kwarg]:
        ...


ErrorStrategy = Union[Literal["new"], Literal["underlying"], Literal["neither"]]
ProxyStrategy = Union[
    Literal["forward"], Literal["backward"], Literal["both"], Literal["neither"]
]


def uplift(
    cls: UpliftableEventEmitterFactoryP[Event, Arg, Kwarg],
    underlying: UpliftedEventEmitterP[Event, Arg, Kwarg],
    error_handling: ErrorStrategy = "new",
    proxy_new_listener: ProxyStrategy = "forward",
    *args: Any,
    **kwargs: Any
):
    """A helper to create instances of an event emitter ``cls`` that inherits
    event behavior from an ``underlying`` event emitter instance.

    This is mostly helpful if you have a simple underlying event emitter
    that you don't have direct control over, but you want to use that
    event emitter in a new context - for example, you may want to ``uplift`` a
    ``EventEmitter`` supplied by a third party library into an
    ``AsyncIOEventEmitter`` so that you may register async event handlers
    in your ``asyncio`` app but still be able to receive events from the
    underlying event emitter and call the underlying event emitter's existing
    handlers. This trick will also often work for a deprecated
    ``EventEmitter`` instance.

    When called, ``uplift`` instantiates a new instance of ``cls``, passing
    along any unrecognized arguments, and overwrites the ``emit`` method on
    the ``underlying`` event emitter to also emit events on the new event
    emitter and vice versa. In both cases, they return whether the ``emit``
    method was handled by either emitter. Execution order prefers the event
    emitter on which ``emit`` was called.

    ``uplift`` also adds an ``unwrap`` method to both instances, either of
    which will unwrap both ``emit`` methods when called.

    The ``error_handling`` flag can be configured to control what happens to
    unhandled errors:

    - 'new': Error handling for the new event emitter is always used and the
      underlying library's non-event-based error handling is inert.
    - 'underlying': Error handling on the underlying event emitter is always
      used and the new event emitter can not implement non-event-based error
      handling.
    - 'neither': Error handling for the new event emitter is used if the
      handler was registered on the new event emitter, and vice versa.

    Tuning this option can be useful depending on how the underlying event
    emitter does error handling. The default is 'new'.

    The ``proxy_new_listener`` option can be configured to control how
    ``new_listener`` events are treated:

    - 'forward': ``new_listener`` events are propagated from the underlying
    - 'both': ``new_listener`` events are propagated as with other events.
    - 'neither': ``new_listener`` events are only fired on their respective
      event emitters.
      event emitter to the new event emitter but not vice versa.
    - 'backward': ``new_listener`` events are propagated from the new event
      emitter to the underlying event emitter, but not vice versa.

    Tuning this option can be useful depending on how the ``new_listener``
    event is used by the underlying event emitter, if at all. The default is
    'forward', since ``underlying`` may not know how to handle certain
    handlers, such as asyncio coroutines.

    Each event emitter tracks its own internal table of handlers.
    ``remove_listener``, ``remove_all_listeners`` and ``listeners`` all
    work independently. This means you will have to remember which event
    emitter an event handler was added to!

    Note that both the new event emitter returned by ``cls`` and the
    underlying event emitter should inherit from ``EventEmitter``, or at
    least implement the interface for the undocumented ``_call_handlers`` and
    ``_emit_handle_potential_error`` methods.
    """

    (
        new_proxy_new_listener,
        underlying_proxy_new_listener,
    ) = _PROXY_NEW_LISTENER_SETTINGS[proxy_new_listener]

    new: UpliftedEventEmitterP[Event, Arg, Kwarg] = cls(*args, **kwargs)

    uplift_error_handlers: Dict[
        str,
        Tuple[
            UpliftedEventEmitterP[Event, Arg, Kwarg],
            UpliftedEventEmitterP[Event, Arg, Kwarg],
        ],
    ] = dict(
        new=(new, new), underlying=(underlying, underlying), neither=(new, underlying)
    )

    new_error_handler, underlying_error_handler = uplift_error_handlers[error_handling]

    _wrap(new, underlying, new_error_handler, new_proxy_new_listener)
    _wrap(underlying, new, underlying_error_handler, underlying_proxy_new_listener)

    return new
