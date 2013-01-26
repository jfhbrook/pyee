# -*- coding: utf-8 -*-

from collections import defaultdict

__all__ = ['EventEmitter', 'Event_emitter']


class EventEmitter(object):
    def __init__(self):
        """
        Initializes the EE.
        """
        self._events = defaultdict(list)

    def on(self, event, f=None):
        """
        Returns a function that takes an event listener callback
        """
        def _on(f):
            #fire 'new_listener' *before* adding the new listener!
            self.emit('new_listener', event, f)

            # Add the necessary function
            self._events[event].append(f)

            # Return original function so removal works
            return f

        if f is None:
            return _on
        else:
            return _on(f)

    def emit(self, event, *args, **kwargs):
        """
        Emit `event`, passing *args to each attached function.
        """
        handled = False
        # Pass the args to each function in the events dict
        for f in self._events[event]:
            f(*args, **kwargs)
            handled = True

        if not handled and event == 'error':
            raise Exception("Uncaught, 'error' event.")
        return handled

    def once(self, event, f=None):
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
        """
        Remove the function attached to `event`.
        """
        self._events[event].remove(f)

    def remove_all_listeners(self, event=None):
        """Remove all listeners attached to `event`. 
        """
        if event is not None:
            self._events[event] = []
        else:
            self._events = None
            self._events = defaultdict(list)

    def listeners(self, event):
        return self._events[event]


# Backwards capatiablity
Event_emitter = EventEmitter
