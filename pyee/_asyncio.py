# -*- coding: utf-8 -*-

from asyncio import ensure_future, Future, iscoroutine
from pyee._base import BaseEventEmitter

__all__ = ['AsyncIOEventEmitter']


class AsyncIOEventEmitter(BaseEventEmitter):
    """An event emitter class which can run asyncio coroutines in addition to
    synchronous blocking functions.

    Unlike the case with synchronous functions, exceptions raised by asyncio
    coroutines are automatically emitted on the ``error`` event.

    When ``loop`` is specified, the supplied event loop will be used when
    scheduling work with ``ensure_future``. Otherwise, the default asyncio
    event loop is used.
    """
    def __init__(self, loop=None):
        super(AsyncIOEventEmitter, self).__init__()
        self._loop = loop

    def on(self, event, f=None):
        """Registers the function (or optionally an asyncio coroutine function)
        ``f`` to the event name ``event``.

        If ``f`` isn't provided, this method returns a function that
        takes ``f`` as a callback; in other words, you can use this method
        as a decorator, like so::

            @ee.on('data')
            def data_handler(data):
                print(data)

        As mentioned, this method can also take an asyncio coroutine function::

           @ee.on('data')
           async def data_handler(data)
               await do_async_thing(data)


        This will automatically schedule the coroutine using
        ``asyncio.ensure_future`` and the configured event loop (defaults to
        ``asyncio.get_event_loop()``).

        In both the decorated and undecorated forms, the event handler is
        returned. The upshot of this is that you can call decorated handlers
        directly, as well as use them in remove_listener calls.
        """
        return super(AsyncIOEventEmitter, self).on(event, f)

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
        In other words, you do not have to await any results from emit, and the
        coroutine is scheduled in a fire-and-forget fashion. Asynchronous
        errors are automatically emitted on the ``error`` event.
        """

        super(AsyncIOEventEmitter, self).emit(event, *args, **kwargs)
