# -*- coding: utf-8 -*-

from pyee._base import BaseEventEmitter

try:
    from concurrent.futures import ThreadPoolExecutor
except ImportError:
    from futures import ThreadPoolExecutor

__all__ = ['ExecutorEventEmitter']


class ExecutorEventEmitter(BaseEventEmitter):
    """An event emitter class which runs handlers in a ``concurrent.futures``
    executor. If using python 2, this will fall back to trying to use the
    ``futures`` backported library (caveats there apply).

    By default, this class creates a default ``ThreadPoolExecutor``, but
    a custom executor may also be passed in explicitly to, for instance,
    use a ``ProcessPoolExecutor`` instead.

    This class runs all emitted events on the configured executor. Errors
    captured by the resulting Future are automatically emitted on the
    ``error`` event. This is unlike the BaseEventEmitter, which have no error
    handling.

    The underlying executor may be shut down by calling the ``shutdown``
    method. Alternately you can treat the event emitter as a context manager::

        with ExecutorEventEmitter() as ee:
            # Underlying executor open

            @ee.on('data')
            def handler(data):
                print(data)

            ee.emit('event')

        # Underlying executor closed

    Since the function call is scheduled on an executor, emit is always
    non-blocking.

    No effort is made to ensure thread safety, beyond using an executor.
    """
    def __init__(self, executor=None):
        super(ExecutorEventEmitter, self).__init__()
        if executor:
            self._executor = executor
        else:
            self._executor = ThreadPoolExecutor()

    def _emit_run(self, f, args, kwargs):
        future = self._executor.submit(f, *args, **kwargs)

        @future.add_done_callback
        def _callback(f):
            exc = f.exception()
            if exc:
                self.emit('error', exc)

    def shutdown(self, wait=True):
        """Call ``shutdown`` on the internal executor."""

        self._executor.shutdown(wait=wait)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.shutdown()
