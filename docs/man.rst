pyee
====

pyee is a rough port of
`node.js's EventEmitter <https://nodejs.org/api/events.html>`_. Unlike its
namesake, it includes a number of subclasses useful for implementing async
and threaded programming in python, such as async/await as seen in python 3.5+.

Install
-------

You can install this project into your environment of choice using ``pip``::

    pip install pyee

Usage
-----

pyee supplies a ``EventEmitter`` class that is similar to the
``EventEmitter`` class from Node.js. In addition, it supplies subclasses for
``asyncio``, ``twisted``, ``concurrent.futures`` and ``trio``, as supported
by the environment.


Example
-------

::

    In [1]: from pyee.base import EventEmitter

    In [2]: ee = EventEmitter()

    In [3]: @ee.on('event')
       ...: def event_handler():
       ...:     print('BANG BANG')
       ...:

    In [4]: ee.emit('event')
    BANG BANG

    In [5]:


API
---

pyee contains a number of modules, each intended for a different concurrency
paradigm or framework:

- ``pyee`` - synchronous ``EventEmitter``, like Node.js
- ``pyee.asyncio`` - asyncio support
- ``pyee.twisted`` - twisted support
- ``pyee.executor`` - concurrent.futures support
- ``pyee.trio`` - trio support

In addition, it contains two experimental modules:

- ``pyee.uplift`` - support for "uplifting" event emitters from one paradigm
  to another - ie., adopting synchronous event emitters for use with asyncio
- ``pyee.cls`` - support for "evented classes", which call class methods on
  events

For in-depth API documentation, visit `the docs on readthedocs.io <https://pyee.rtfd.io>`_.

Links
-----

* `Fork Me On GitHub! <https://github.com/jfhbrook/pyee>`_
* `The Docs on readthedocs.io <https://pyee.rtfd.io>`_
