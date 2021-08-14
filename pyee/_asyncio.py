# -*- coding: utf-8 -*-

from asyncio import ensure_future, Future, iscoroutine
from pyee._base import EventEmitter

__all__ = ["AsyncIOEventEmitter"]


class AsyncIOEventEmitter(EventEmitter):
    """An event emitter class which can run asyncio coroutines in addition to
    synchronous blocking functions. For example::

        @ee.on('event')
        async def async_handler(*args, **kwargs):
            await returns_a_future()

    On emit, the event emitter  will automatically schedule the coroutine using
    ``asyncio.ensure_future`` and the configured event loop (defaults to
    ``asyncio.get_event_loop()``).

    Unlike the case with the BaseEventEmitter, all exceptions raised by
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

    def __init__(self, loop=None):
        super(AsyncIOEventEmitter, self).__init__()
        self._loop = loop

    def _emit_run(self, f, args, kwargs):
        try:
            coro = f(*args, **kwargs)
        except Exception as exc:
            self.emit("error", exc)
        else:
            if iscoroutine(coro):
                if self._loop:
                    f = ensure_future(coro, loop=self._loop)
                else:
                    f = ensure_future(coro)
            elif isinstance(coro, Future):
                f = coro
            else:
                f = None

            if f:

                @f.add_done_callback
                def _callback(f):
                    if f.cancelled():
                        return

                    exc = f.exception()
                    if exc:
                        self.emit("error", exc)
