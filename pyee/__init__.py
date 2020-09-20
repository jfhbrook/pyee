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

from pyee._base import (
    EventEmitter,
    PyeeException
)


class BaseEventEmitter(EventEmitter):
    def __init__(self):
        warn(DeprecationWarning(
            'pyee.BaseEventEmitter is deprecated and will be removed in a '
            'future major version; you should instead use pyee.EventEmitter.'
        ))

        super(BaseEventEmitter, self).__init__()


__all__ = ['BaseEventEmitter', 'EventEmitter', 'PyeeException']

try:
    from pyee._asyncio import AsyncIOEventEmitter  # noqa
    __all__.append('AsyncIOEventEmitter')
except ImportError:
    pass

try:
    from pyee._twisted import TwistedEventEmitter  # noqa
    __all__.append('TwistedEventEmitter')
except ImportError:
    pass

try:
    from pyee._executor import ExecutorEventEmitter  # noqa
    __all__.append('ExecutorEventEmitter')
except ImportError:
    pass

try:
    from pyee._trio import TrioEventEmitter  # noqa
    __all__.append('TrioEventEmitter')
except (ImportError, SyntaxError):
    pass
