# -*- coding: utf-8 -*-

from pyee._base import BaseEventEmitter

from twisted.internet.defer import Deferred, ensureDeferred

try:
    from asyncio import iscoroutine
except ImportError:
    iscoroutine = None


__all__ = ['TwistedEventEmitter']


class TwistedEventEmitter(BaseEventEmitter):
    """An event emitter class which can run twisted coroutines and handle
    returned Deferreds, in addition to synchronous blocking functions. For
    example::

        @ee.on('event')
        @inlineCallbacks
        def async_handler(*args, **kwargs):
            yield returns_a_deferred()

    or::

        @ee.on('event')
        async def async_handler(*args, **kwargs):
            await returns_a_deferred()


    When async handlers fail, Failures are first emitted on the ``failure``
    event. If there are no ``failure`` handlers, the Failure's associated
    exception is then emitted on the ``error`` event. If there are no ``error``
    handlers, the exception is raised.
    """
    def __init__(self):
        super(TwistedEventEmitter, self).__init__()

    def _emit_run(self, f, args, kwargs):
        result = f(*args, **kwargs)
        if iscoroutine and iscoroutine(result):
            d = ensureDeferred(result)
        elif isinstance(result, Deferred):
            d = result
        else:
            d = None

        if d:
            @d.addErrback
            def _errback(failure):
                if failure:
                    self.emit('failure', failure)

    def _emit_handle_potential_error(self, event, error):
        if event == 'failure':
            self.emit('error', error.value)
        else:
            (
                super(TwistedEventEmitter, self)
            )._emit_handle_potential_error(event, error)

    def emit(self, event, *args, **kwargs):
        """Emit ``event``, passing ``*args`` and ``**kwargs`` to each attached
        function. Returns ``True`` if any functions are attached to ``event``;
        otherwise returns ``False``.

        For twisted coroutine event handlers, calling emit is non-blocking.
        In other words, you do not have to await any results from emit, and the
        coroutine is scheduled in a fire-and-forget fashion. Asynchronous
        errors are automatically emitted on the ``error`` event.

        Similar behavior occurs for "sync" functions which return Deferreds.
        """

        return super(TwistedEventEmitter, self).emit(event, *args, **kwargs)
