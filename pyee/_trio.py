# -*- coding: utf-8 -*-

from contextlib import asynccontextmanager
import trio
from pyee._base import BaseEventEmitter, PyeeException

__all__ = ['TrioEventEmitter']


class TrioEventEmitter(BaseEventEmitter):
    """An event emitter class which can run trio tasks in a trio nursery.

    By default, this class will lazily create both a nursery manager (the
    object returned from ``trio.open_nursery()`` and a nursery (the object
    yielded by using the nursery manager as an async context manager). It is
    also possible to supply an existing nursery manager via the ``manager``
    argument, or an existing nursery via the ``nursery`` argument.

    Instances of TrioEventEmitter are themselves async context managers, so
    that they may manage the lifecycle of the underlying trio nursery. For
    example, typical usage of this library may look something like this::

        async with TrioEventEmitter() as ee:
            # Underlying nursery is instantiated and ready to go
            @ee.on('data')
            async def handler(data):
                print(data)

            ee.emit('event')

        # Underlying nursery and manager have been cleaned up

    Unlike the case with the BaseEventEmitter, all exceptions raised by event
    handlers are automatically emitted on the ``error`` event. This is
    important for trio coroutines specifically but is also handled for
    synchronous functions for consistency.

    For trio coroutine event handlers, calling emit is non-blocking. In other
    words, you should not attempt to await emit; the coroutine is scheduled
    in a fire-and-forget fashion.
    """
    def __init__(self, nursery=None, manager=None):
        super(TrioEventEmitter, self).__init__()
        if nursery:
            if manager:
                raise PyeeException(
                    'You may either pass a nursery or a nursery manager '
                    'but not both'
                )
            self._nursery = nursery
            self._manager = None
        elif manager:
            self._nursery = None
            self._manager = manager
        else:
            self._manager = trio.open_nursery()

    def _async_runner(self, f, args, kwargs):
        async def runner():
            try:
                await f(*args, **kwargs)
            except Exception as exc:
                self.emit('error', exc)

        return runner

    def _emit_run(self, f, args, kwargs):
        self._nursery.start_soon(self._async_runner(f, args, kwargs))

    @asynccontextmanager
    async def context(self):
        """Returns an async contextmanager which manages the underlying
        nursery to the EventEmitter. The ``TrioEventEmitter``'s
        async context management methods are implemented using this
        function, but it may also be used directly for clarity.
        """
        if getattr(self, '_nursery', None):
            yield self._nursery
        else:
            async with self._manager as nursery:
                self._nursery = nursery
                yield self

    async def __aenter__(self):
        self._context = self.context()
        return await self._context.__aenter__()

    async def __aexit__(self, type, value, traceback):
        rv = await self._context.__aexit__(type, value, traceback)
        self._context = None
        self._nursery = None
        self._manager = None
        return rv
