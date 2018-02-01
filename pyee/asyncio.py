# -*- coding: utf-8 -*-

from asyncio import ensure_future, Future, iscoroutine
from pyee.base import EventEmitter

__all__ = ['AsyncIOEventEmitter']


class AsyncIOEventEmitter(EventEmitter):
    """An event emitter class which can run asyncio coroutines in addition to
    synchronous blocking functions.

    Unlike the case with synchronous functions, exceptions raised by asyncio
    coroutines are automatically emitted on the ``error`` event.
    """
    def __init__(self, loop=None):
        super().__init__()
        self._loop = loop

    def _emit_run(self, f, args, kwargs):
        coro = f(*args, **kwargs)

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
                exc = f.exception()
                if exc:
                    self.emit('error', exc)

    def emit(self, event, *args, **kwargs):
        """Emit ``event``, passing ``*args`` and ``**kwargs`` to each attached
        function. Returns ``True`` if any functions are attached to ``event``;
        otherwise returns ``False``.

        For asyncio coroutine event handlers, calling emit is non-blocking.
        In other ords, you do not have to await any results from emit, and the
        coroutine is scheduled in a fire-and-forget fashion. Asynchronous
        errors are automatically emitted on the ``error`` event.
        """

        super().emit(event, *args, **kwargs)
