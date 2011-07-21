class Event_emitter(object):
    def __init__(self):
        """
        Initializes the EE.
        """
        self._events = { 'new_listener': [] }

    def on(self, event, f=None):
        """
        Returns a function that takes an event listener callback
        """
        def _on(f):
            # Creating a new event array if necessary
            try:
                self._events[event]
            except KeyError:
                self._events[event] = []

            #fire 'new_listener' *before* adding the new listener!
            self.emit('new_listener')

            # Add the necessary function
            self._events[event].append(f)

        if (f==None):
            return _on
        else:
            return _on(f)

    def emit(self, event, *args):
        """
        Emit `event`, passing *args to each attached function.
        """

        # Pass the args to each function in the events dict
        for fxn in self._events[event]:
            fxn(*args)

    def once(self, event, f=None):
        def _once(f):
            def g(*args, **kwargs):
                f(*args, **kwargs)
                self.remove_listener(self,event)
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
