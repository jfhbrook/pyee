# -*- coding: utf-8 -*-

"""
pyee supplies an ``EventEmitter`` class similar to the ``EventEmitter``
from Node.js. In addition, it supplies the subclasses ``AsyncIOEventEmitter``,
``TwistedEventEmitter`` and ``ExecutorEventEmitter`` for supporting async and
threaded execution with asyncio, twisted, and concurrent.futures Executors
respectively, as supported by the environment.


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

from pyee._base import EventEmitter, PyeeException

__all__ = ['EventEmitter', 'PyeeException']

try:
    from pyee._asyncio import AsyncIOEventEmitter  # noqa
    __all__.append('AsyncIOEventEmitter')
except ImportError:
    pass

from pyee._twisted import TwistedEventEmitter  # noqa
__all__.append('TwistedEventEmitter')

try:
    from pyee._executor import ExecutorEventEmitter  # noqa
    __all__.append('ExecutorEventEmitter')
except ImportError:
    pass
