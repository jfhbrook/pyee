# -*- coding: utf-8 -*-

"""
pyee supplies a ``BaseEventEmitter`` class that is similar to the
``EventEmitter`` class from Node.js. In addition, it supplies the subclasses
``AsyncIOEventEmitter``, ``TwistedEventEmitter`` and ``ExecutorEventEmitter``
for supporting async and threaded execution with asyncio, twisted, and
concurrent.futures Executors respectively, as supported by the environment.


Example
-------

::

    In [1]: from pyee import BaseEventEmitter

    In [2]: ee = BaseEventEmitter()

    In [3]: @ee.on('event')
       ...: def event_handler():
       ...:     print('BANG BANG')
       ...:

    In [4]: ee.emit('event')
    BANG BANG

    In [5]:

"""

import importlib
from pyee._base import (
    BaseEventEmitter,
    PyeeException,
    UnspecifiedErrorException
)
from pyee._compat import CompatEventEmitter


class LazyImportException(PyeeException):
    '''
    Subclasses of BaseEventEmitter that require other installed functionality
    are loaded lazily so that meaningful errors can be raised when importing
    them rather than having the imports be spookily missing from the
    module.

    This exception is raised when a lazy-loaded module can't be imported.
    The reason an 'ImportError' or an 'AttributeError' isn't being raised
    instead is that the former is normally raised when importing from while
    the latter is raised when accessing properties on an imported module
    object, but the lazy loading system can't tell which is which. Moreover,
    the error message can not be customized when inheriting from either.
    '''


LAZY_IMPORTS = {
    'TwistedEventEmitter': dict(
        path=('pyee._twisted', 'TwistedEventEmitter'),
        message="in order to use 'TwistedEventEmitter', you need to have a "
        'version of twisted installed that supports coroutines'
    ),
    'AsyncIOEventEmitter': dict(
        path=('pyee._asyncio', 'AsyncIOEventEmitter'),
        message="in order to use 'AsyncIOEventEmitter', you must be using at "
        "least python 3.4 and have the 'asyncio' library available, and if "
        "you want to use async/await you should be using at least python 3.5"
    ),
    'ExecutorEventEmitter': dict(
        path=('pyee._executor', 'ExecutorEventEmitter'),
        message="in order to use 'ExecutorEventEmitter', you must either be "
        "using at least python 3.2 and have the 'concurrent.futures' library "
        "available, or have the 'futures' polyfill installed"
    )
}

BASE_IMPORTS = {
    'BaseEventEmitter': BaseEventEmitter,
    'EventEmitter': CompatEventEmitter,
    'PyeeException': PyeeException,
    'UnspecifiedErrorException': UnspecifiedErrorException,
    'LazyImportException': LazyImportException
}


__all__ = list(BASE_IMPORTS) + list(LAZY_IMPORTS.keys())


def __getattr__(name):
    if name in BASE_IMPORTS:
        return BASE_IMPORTS[name]
    elif name in LAZY_IMPORTS:
        try:
            path = LAZY_IMPORTS[name]['path']
            return getattr(importlib.import_module(path[0]), path[1])
        except ImportError as exc:
            hint = LAZY_IMPORTS[name]['message']
            raise LazyImportException(hint) from exc
    else:
        # This one is safe because python checks __all__ before calling
        # __getattr__ when importing from package
        nice_message = f"module 'pyee' has no attribute '{name}'"
        raise AttributeError(nice_message)
