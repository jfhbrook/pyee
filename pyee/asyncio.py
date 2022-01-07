# -*- coding: utf-8 -*-

from asyncio import AbstractEventLoop, ensure_future, Future, iscoroutine
from typing import Any, Dict, Optional, Tuple, Union

from pyee.base import (
    AnyHandlerP,
    Arg,
    Event,
    EventEmitter,
    HandlerP,
    InternalEvent,
    Kwarg,
)

__all__ = ["AsyncIOEventEmitter"]


class AsyncIOEventEmitter(EventEmitter[Event, Arg, Kwarg]):
    """An event emitter class which can run asyncio coroutines in addition to
    synchronous blocking functions. For example::

        @ee.on('event')
        async def async_handler(*args, **kwargs):
            await returns_a_future()

    On emit, the event emitter  will automatically schedule the coroutine using
    ``asyncio.ensure_future`` and the configured event loop (defaults to
    ``asyncio.get_event_loop()``).

    Unlike the case with the EventEmitter, all exceptions raised by
    event handlers are automatically emitted on the ``error`` event. This is
    important for asyncio coroutines specifically but is also handled for
    synchronous functions for consistency.

    When ``loop`` is specified, the supplied event loop will be used when
    scheduling work with ``ensure_future``. Otherwise, the default asyncio
    event loop is used.

    For asyncio coroutine event handlers, calling emit is non-blocking.
    In other words, you do not have to await any results from emit, and the
    coroutine is scheduled in a fire-and-forget fashion.
    """

    def __init__(self, loop: Optional[AbstractEventLoop] = None):
        super(AsyncIOEventEmitter, self).__init__()
        self._loop: Optional[AbstractEventLoop] = loop

    def _emit_run(
        self,
        f: HandlerP[Event, Arg, Kwarg],
        args: Tuple[Union[Arg, Exception, Event, InternalEvent, AnyHandlerP], ...],
        kwargs: Dict[str, Kwarg],
    ):
        try:
            coro: Any = f(*args, **kwargs)
        except Exception as exc:
            self.emit("error", exc)
        else:
            if iscoroutine(coro):
                if self._loop:
                    fut: Future = ensure_future(coro, loop=self._loop)
                else:
                    fut = ensure_future(coro)
            elif isinstance(coro, Future):
                fut = coro
            else:
                return

            def callback(f):
                if f.cancelled():
                    return

                exc: Exception = f.exception()
                if exc:
                    self.emit("error", exc)

            fut.add_done_callback(callback)