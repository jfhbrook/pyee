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
    ``TrioEventEmitter`` or ``BaseEventEmitter``.

    This class is similar to the ``AsyncIOEventEmitter`` class, but also allows
    for overriding the scheduler function (``ensure_future`` by default as in
    ``ASyncIOEventEmitter``) and does duck typing checks to handle Deferreds.
    In other words, by setting ``scheduler`` to
    ``twisted.internet.defer.ensureDeferred`` this will support twisted use
    cases for coroutines.

    When calling synchronous handlers, raised exceptions are ignored - as with
    the BaseEventEmitter, you must capture and handle your own exceptions.
    However, for coroutine functions, exceptions are handled by emitting them
    on the ``error`` event.  Note that when using with twisted, the ``error``
    event will emit Failures, not Exceptions.

    This class will also successfully import in python 2, but without coroutine
    support.
    """

    def __init__(self, scheduler=ensure_future, loop=None):
        warn(DeprecationWarning(
            'pyee.EventEmitter is deprecated and will be removed in a future '
            'major version; you should instead use either '
            'pyee.AsyncIOEventEmitter, pyee.TwistedEventEmitter, '
            'pyee.ExecutorEventEmitter, pyee.TrioEventEmitter, '
            'or pyee.BaseEventEmitter.'
        ))

        super(CompatEventEmitter, self).__init__()

        self._schedule = scheduler
        self._loop = loop

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
