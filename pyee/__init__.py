# -*- coding: utf-8 -*-
"""
pyee
====

pyee supplies an ``EventEmitter`` object similar to the ``EventEmitter``
from Node.js.

There is also the possibility to use mqtt topic patterns to match events

Example
-------

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

    In [6]: ee.on('a/#/c', lambda ...)

Easy-peasy.


"""


from collections import defaultdict

__all__ = ['EventEmitter', 'Event_emitter']


class EventEmitter(object):

    """The EventEmitter class.

    (Special) Events
    ----------------

    -   'new_listener': Fires whenever a new listener is created. Listeners for this
    event do not fire upon their own creation.

    -   'error': When emitted raises an Exception by default, behavior can be overriden by
    attaching callback to the event.

    For example::

        @ee.on('error')
        def onError(message):
            logging.err(message)

        ee.emit('error', Exception('something blew up'))

    """

    def __init__(self):
        """
        Initializes the EE.
        """
        self._events = defaultdict(list)

        # Specialised dict for pattern matching topics
        # This way it will not impact standard behaviour
        self._patterns = defaultdict(list)

    def on(self, event, f=None):
        """Registers the function ``f`` to the event name ``event``.

        If ``f`` isn't provided, this method returns a function that
        takes ``f`` as a callback; in other words, you can use this method
        as a decorator, like so:

            @ee.on('data')
            def data_handler(data):
                print data

        """

        def _on(f):
            # Fire 'new_listener' *before* adding the new listener!
            self.emit('new_listener', event, f)

            # Add the necessary function
            if '#' in event:
                self._patterns[event].append(f)
            else:
                self._events[event].append(f)

            # Return original function so removal works
            return f

        if f is None:
            return _on
        else:
            return _on(f)

    def emit(self, event, *args, **kwargs):
        """Emit ``event``, passing ``*args`` to each attached function. Returns
        ``True`` if any functions are attached to ``event``; otherwise returns
        ``False``.

        Example:

            ee.emit('data', '00101001')

        Assuming ``data`` is an attached function, this will call
        ``data('00101001')'``.

        """
        handled = False

        for p in self._patterns:
            if self._matches(p, event):
                for f in self._patterns[p]:
                    f(*args, **kwargs)
                    handled = True

        # Pass the args to each function in the events dict
        for f in self._events[event]:
            f(*args, **kwargs)
            handled = True

        if not handled and event == 'error':
            raise Exception("Uncaught 'error' event.")

        return handled

    def _matches(self, pattern, event):
        """
        Check that 'a/#/b/#/c' pattern matches '/a/x/b/x/c'
        """

        ps, es = pattern.split('/'), event.split('/')
        return all([x == y or x == '#' for x, y in zip(ps, es)]) and len(ps) <= len(es)

    def once(self, event, f=None):
        """The same as ``ee.on``, except that the listener is automatically
        removed after being called.
        """
        def _once(f):
            def g(*args, **kwargs):
                f(*args, **kwargs)
                self.remove_listener(event, g)
            return g

        if f is None:
            return lambda f: self.on(event, _once(f))
        else:
            self.on(event, _once(f))

    def remove_listener(self, event, f):
        """Removes the function ``f`` from ``event``.

        Requires that ``f`` is not closed over by ``ee.on``. (In other words,
        it is, unfortunately, not possible to use this with the decorator
        style is.)

        """
        if '#' in event:
            self._patterns[event].remove(f)
        else:
            self._events[event].remove(f)

    def remove_all_listeners(self, event=None):
        """Remove all listeners attached to ``event``.
        """
        if event is not None:
            if '#' in event:
                self._patterns[event] = []
            else:
                self._events[event] = []
        else:
            self._events = None
            self._patterns = None
            self._events = defaultdict(list)
            self._patterns = defaultdict(list)

    def listeners(self, event):
        """Returns the list of all listeners registered to the ``event``.
        """
        return self._events[event] if not '#' in event else self._patterns[event]

# Backwards compatiblity
Event_emitter = EventEmitter
