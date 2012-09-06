pyee
======

pyee supplies an ``EventEmitter`` object similar to the ``EventEmitter``
from Node.js.

Example:
--------

::

    In [1]: from pyee import EventEmitter

    In [2]: ee = EventEmitter()

    In [3]: @ee.on('event')
       ...: def event_handler():
       ...:     print 'BANG BANG'
       ...:

    In [4]: ee.emit('event')
    BANG BANG

    In [5]:

Easy-peasy.


Installation:
-------------

::

    sudo pip install pyee

Methods:
--------

**ee.on(event, f=None)**: Registers the function ``f`` to the event name
``event``. Example::

    ee.on('data', some_fxn)

If ``f`` is not specified, ``ee.on`` returns a function that takes ``f`` as a
callback, which allows for decorator styles::

    @ee.on('data')
    def data_handler(data):
        print data

**ee.emit(event, *args, **kwargs)**: Emits the event, calling the attached functions
with ``*args``. For example::

    ee.emit('data', '00101001')

This will call ``data('00101001')'`` (assuming ``data`` is an attached function).
Returns ``False`` if no functions are attached to handle the emission (otherwise ``True``).

**ee.once(event, f=None)**: The same as ``ee.on``, except that the listener
is automatically removed after it's called.

**ee.remove_listener(event, fxn)**: Removes the function ``fxn`` from ``event``.
Requires that the function is not closed over by ``ee.on`` (using this with the
decorator style is unfortunately not possible).

**ee.remove_all_listeners(event)**: Removes all listeners from ``event``.

**ee.listeners(event)**: Returns the array of all listeners registered to
the given ``event``.


(Special) Events:
-------

**"new_listener"**: Fires whenever a new listener is created. Listeners for this
event do not fire upon their own creation.

**"error"**: When emitted raises an Exception by default, behavior can be overriden by
attaching callback to the event. For example::

    @ee.on('error')
    def onError(message):
        logging.err(message)

    ee.emit('error', 'something blew up')

Tests:
------

::

    nosetests

Developers! Developers! Developers!
-----------------------------------

If you're a Python and/or Node.js fan, and you like what you see (or don't quite like
what you see): I heartily invite you to dig in, fork it up and `git push it
good <https://twitter.com/#!/maraksquires/status/71911996051824640>`_.

License:
--------

MIT.
