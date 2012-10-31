# -*- coding: utf-8 -*-
# FIXME: Add module docstring

__all__ = ['EventEmitter', 'Event_emitter']

from collections import defaultdict


class EventEmitter(object):
    # FIXME: Add docstring
    
    def __init__(self):
        '''Initializes the EE.'''
        self._events = defaultdict(list)

    def on(self, event, fn=None):
        '''Function decorator.  Decorate a function with this to have it fire
        whenever `event` is emitted.
        '''
        def _on(fn):
            # Fire `new_listener` *before* adding the new listener!
            self.emit('new_listener', event, fn)

            # Add the necessary function
            self._events[event].append(fn)

            # Return original function so removal works
            return fn

        if fn is None:
            return _on
        else:
            return _on(fn)

    def emit(self, event, *args, **kwargs):
        '''Emit `event`, passing `*args` to each attached function.'''
        handled = False
        # Pass the args to each function in the events dict
        for fxn in self._events[event]:
            fxn(*args, **kwargs)
            handled = True

        if not handled and event == 'error':
            raise Exception("Uncaught 'error' event.")

        return handled

    def once(self, event, f=None):
        # FIXME: add docstring
        def _once(f):
            def g(*args, **kwargs):
                f(*args, **kwargs)
                self.remove_listener(event, g)
            return g

        if f is None:
            return lambda f: self.on(event, _once(f))
        else:
            self.on(event, _once(f))

    def remove_listener(self, event, function):
        '''Remove listener `function` from `event`.'''
        self._events[event].remove(function)

    def remove_all_listeners(self, event=None):
        '''Remove all listeners attached to `event`.'''
        if event is not None:
            self._events[event] = []
        else:
            self._events = None
            self._events = defaultdict(list)

    def listeners(self, event):
        '''Return all listeners for `event`.'''
        # FIXME: specify the kind of object that is returned
        return self._events[event]


# Backwards capatiablity
Event_emitter = EventEmitter