from collections import defaultdict

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

        if (f==None):
            return _on
        else:
            return _on(f)

    def emit(self, event, *args, **kwargs):
        """
        Emit `event`, passing *args to each attached function.
        """
        handled = False
        # Pass the args to each function in the events dict
        for fxn in self._events[event]:
            fxn(*args, **kwargs)
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

        if (f==None):
            return lambda f: self.on(event, _once(f))
        else:
            self.on(event, _once(f))


    def remove_listener(self, event, function):
        """
        Remove the function attached to `event`.
        """
        self._events[event].remove(function)

    def remove_all_listeners(self, event):
        """
        Remove all listeners attached to `event`.
        """
        self._events[event] = []

    def listeners(self, event):
        return self._events[event]

# Backwards capatiablity
Event_emitter = EventEmitter
__all__ = ['Event_emitter', 'EventEmitter']
