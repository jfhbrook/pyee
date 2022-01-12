pyee
====

pyee is a rough port of
`node.js's EventEmitter <https://nodejs.org/api/events.html>`_. Unlike its
namesake, it includes a number of subclasses useful for implementing async
and threaded programming in python, such as async/await as seen in python 3.5+.

Install:
--------

You can install this project into your environment of choice using ``pip``::

    pip install pyee

API Docs:
---------

.. toctree::
   :maxdepth: 2

.. automodule:: pyee

.. autoclass:: pyee.EventEmitter
    :members:

.. autoclass:: pyee.asyncio.AsyncIOEventEmitter
    :members:

.. autoclass:: pyee.twisted.TwistedEventEmitter
    :members:

.. autoclass:: pyee.executor.ExecutorEventEmitter
    :members:

.. autoclass:: pyee.trio.TrioEventEmitter
    :members:

.. autoclass:: BaseEventEmitter
    :members:

.. autoexception:: pyee.PyeeException

.. autofunction:: pyee.uplift.uplift

.. autofunction:: pyee.cls.on

.. autofunction:: pyee.cls.evented


Some Links
==========

* `Fork Me On GitHub! <https://github.com/jfhbrook/pyee>`_
* `These Very Docs on readthedocs.io <https://pyee.rtfd.io>`_
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Changelog
=========

.. include:: ../CHANGELOG.rst
