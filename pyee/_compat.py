from pyee._base import BaseEventEmitter
from warnings import warn

try:
    from asyncio import iscoroutine, ensure_future
except ImportError:
    iscoroutine = None
    ensure_future = None


class CompatEventEmitter(BaseEventEmitter):
    """An EventEmitter exposed for compatibility with prior versions of
    pyee. This functionality is deprecated; you should instead use either
    ``AsyncIOEventEmitter``, ``TwistedEventEmitter``, ``ExecutorEventEmitter``,
    or ``BaseEventEmitter``.

    This class is similar to the ``AsyncIOEventEmitter`` class, but also allows
    for overriding the scheduler function (``ensure_future`` by default as in
    ``ASyncIOEventEmitter``) and does duck typing checks to handle Deferreds.
    In other words, by setting ``scheduler`` to
    ``twisted.internet.defer.ensureDeferred`` this will support twisted use
    cases for coroutines.

    This class will also successfully import in python 2, but without coroutine
    support.
    """

    def __init__(self, scheduler=ensure_future, loop=None):
        warn(DeprecationWarning(
            'pyee.EventEmitter is deprecated and will be removed in a future '
            'major version; you should instead use either '
            'pyee.AsyncIOEventEmitter, pyee.TwistedEventEmitter, '
            'pyee.ExecutorEventEmitter or pyee.BaseEventEmitter.'
        ))

        super(CompatEventEmitter, self).__init__()

        self._schedule = scheduler
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

        This will automatically schedule the coroutine using the configured
        scheduling function (defaults to ``asyncio.ensure_future``) and the
        configured event loop (defaults to ``asyncio.get_event_loop()``).
        In both the decorated and undecorated forms, the event handler is
        returned. The upshot of this is that you can call decorated handlers
        directly, as well as use them in remove_listener calls.
        """

        return super(CompatEventEmitter, self).on(event, f)

    def _emit_run(self, f, args, kwargs):
        coro = f(*args, **kwargs)

        if iscoroutine and iscoroutine(coro):
            if self._loop:
                d = self._schedule(coro, loop=self._loop)
            else:
                d = self._schedule(coro)

            # scheduler gave us an asyncio Future
            if hasattr(d, 'add_done_callback'):
                @d.add_done_callback
                def _callback(f):
                    exc = f.exception()
                    if exc:
                        self.emit('error', exc)

            # scheduler gave us a twisted Deferred
            elif hasattr(d, 'addErrback'):
                @d.addErrback
                def _callback(exc):
                    self.emit('error', exc)

    def emit(self, event, *args, **kwargs):
        """Emit ``event``, passing ``*args`` and ``**kwargs`` to each attached
        function. Returns ``True`` if any functions are attached to ``event``;
        otherwise returns ``False``.

        For coroutine event handlers, calling emit is non-blocking. In other
        words, you do not have to await any results from emit, and the
        coroutine is scheduled in a fire-and-forget fashion. Asynchronous
        errors are automatically emitted on the ``error`` event.
        """
        super(CompatEventEmitter, self).emit(event, *args, **kwargs)
