# -*- coding: utf-8 -*-

"""
pyee supplies a ``EventEmitter`` class that is similar to the
``EventEmitter`` class from Node.js. In addition, it supplies the subclasses
``AsyncIOEventEmitter``, ``TwistedEventEmitter`` and ``ExecutorEventEmitter``
for supporting async and threaded execution with asyncio, twisted, and
concurrent.futures Executors respectively, as supported by the environment.


Example
-------

::

    In [1]: from pyee import EventEmitter

    In [2]: ee = EventEmitter()

    In [3]: @ee.on('event')
       ...: def event_handler():
       ...:     print('BANG BANG')
       ...:

    In [4]: ee.emit('event')
    BANG BANG

    In [5]:

"""

from warnings import warn

from pyee.base import EventEmitter, PyeeException


class BaseEventEmitter(EventEmitter):
    """
    pyee.BaseEventEmitter is deprecated and an alias for pyee.EventEmitter.
    """

    def __init__(self):
        warn(
            DeprecationWarning(
                "pyee.BaseEventEmitter is deprecated and will be removed in a "
                "future major version; you should instead use pyee.EventEmitter."
            )
        )

        super(BaseEventEmitter, self).__init__()


__all__ = ["BaseEventEmitter", "EventEmitter", "PyeeException"]

try:
    from pyee.asyncio import AsyncIOEventEmitter as BaseAsyncIOEventEmitter  # noqa

    class AsyncIOEventEmitter(BaseAsyncIOEventEmitter):
        """
        pyee.AsyncIOEventEmitter is deprecated and an alias for
        pyee.asyncio.AsyncIOEventEmitter.
        """

        def __init__(self, loop=None):
            warn(
                DeprecationWarning(
                    "pyee.AsyncIOEventEmitter is deprecated and will be removed "
                    "in a future major version; you should instead use "
                    "pyee.asyncio.AsyncIOEventEmitter."
                )
            )

            super(AsyncIOEventEmitter, self).__init__(loop=loop)

    __all__.append("AsyncIOEventEmitter")
except ImportError:
    raise

try:
    from pyee.twisted import TwistedEventEmitter as BaseTwistedEventEmitter  # noqa

    class TwistedEventEmitter(BaseTwistedEventEmitter):
        """
        pyee.TwistedEventEmitter is deprecated and an alias for
        pyee.twisted.TwistedEventEmitter.
        """

        def __init__(self):
            warn(
                DeprecationWarning(
                    "pyee.TwistedEventEmitter is deprecated and will be removed "
                    "in a future major version; you should instead use "
                    "pyee.twisted.TwistedEventEmitter."
                )
            )

            super(TwistedEventEmitter, self).__init__()

    __all__.append("TwistedEventEmitter")
except ImportError:
    pass

try:
    from pyee.executor import ExecutorEventEmitter as BaseExecutorEventEmitter  # noqa

    class ExecutorEventEmitter(BaseExecutorEventEmitter):
        """
        pyee.ExecutorEventEmitter is deprecated and an alias for
        pyee.executor.ExecutorEventEmitter.
        """

        def __init__(self, executor=None):
            warn(
                DeprecationWarning(
                    "pyee.ExecutorEventEmitter is deprecated and will be removed "
                    "in a future major version; you should instead use "
                    "pyee.executor.ExecutorEventEmitter."
                )
            )

            super(ExecutorEventEmitter, self).__init__(executor=executor)

    __all__.append("ExecutorEventEmitter")
except ImportError:
    pass

try:
    from pyee.trio import TrioEventEmitter as BaseTrioEventEmitter  # noqa

    class TrioEventEmitter(BaseTrioEventEmitter):
        """
        pyee.TrioEventEmitter is deprecated and an alias for
        pyee.trio.TrioEventEmitter.
        """

        def __init__(self, nursery=None, manager=None):
            warn(
                DeprecationWarning(
                    "pyee.TrioEventEmitter is deprecated and will be removed "
                    "in a future major version; you should instead use "
                    "pyee.trio.TrioEventEmitter."
                )
            )

            super(TrioEventEmitter, self).__init__(nursery=nursery, manager=manager)

    __all__.append("TrioEventEmitter")
except (ImportError, SyntaxError):
    pass
