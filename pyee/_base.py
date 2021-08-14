# -*- coding: utf-8 -*-

from collections import defaultdict, OrderedDict
from threading import Lock

__all__ = ["EventEmitter", "PyeeException"]


class PyeeException(Exception):
    """An exception internal to pyee."""

    pass


class EventEmitter:
    """The base event emitter class. All other event emitters inherit from
    this class.

    Most events are registered with an emitter via the ``on`` and ``once``
    methods, and fired with the ``emit`` method. However, pyee event emitters
    have two *special* events:

    - ``new_listener``: Fires whenever a new listener is created. Listeners for
      this event do not fire upon their own creation.

    - ``error``: When emitted raises an Exception by default, behavior can be
      overriden by attaching callback to the event.

      For example::

          @ee.on('error')
          def on_error(message):
              logging.err(message)

          ee.emit('error', Exception('something blew up'))

    All callbacks are handled in a synchronous, blocking manner. As in node.js,
    raised exceptions are not automatically handled for you---you must catch
    your own exceptions, and treat them accordingly.
    """

    def __init__(self):
        self._events = defaultdict(OrderedDict)
        self._lock = Lock()

    def on(self, event, f=None):
        """Registers the function ``f`` to the event name ``event``.

        If ``f`` isn't provided, this method returns a function that
        takes ``f`` as a callback; in other words, you can use this method
        as a decorator, like so::

            @ee.on('data')
            def data_handler(data):
                print(data)

        In both the decorated and undecorated forms, the event handler is
        returned. The upshot of this is that you can call decorated handlers
        directly, as well as use them in remove_listener calls.
        """

        def _on(f):
            self._add_event_handler(event, f, f)
            return f

        if f is None:
            return _on
        else:
            return _on(f)

    def _add_event_handler(self, event, k, v):
        # Fire 'new_listener' *before* adding the new listener!
        self.emit("new_listener", event, k)

        # Add the necessary function
        # Note that k and v are the same for `on` handlers, but
        # different for `once` handlers, where v is a wrapped version
        # of k which removes itself before calling k
        with self._lock:
            self._events[event][k] = v

    def _emit_run(self, f, args, kwargs):
        f(*args, **kwargs)

    def _emit_handle_potential_error(self, event, error):
        if event == "error":
            if error:
                raise error
            else:
                raise PyeeException("Uncaught, unspecified 'error' event.")

    def _call_handlers(self, event, args, kwargs):
        handled = False

        with self._lock:
            funcs = list(self._events[event].values())
        for f in funcs:
            self._emit_run(f, args, kwargs)
            handled = True

        return handled

    def emit(self, event, *args, **kwargs):
        """Emit ``event``, passing ``*args`` and ``**kwargs`` to each attached
        function. Returns ``True`` if any functions are attached to ``event``;
        otherwise returns ``False``.

        Example::

            ee.emit('data', '00101001')

        Assuming ``data`` is an attached function, this will call
        ``data('00101001')'``.
        """
        handled = self._call_handlers(event, args, kwargs)

        if not handled:
            self._emit_handle_potential_error(event, args[0] if args else None)

        return handled

    def once(self, event, f=None):
        """The same as ``ee.on``, except that the listener is automatically
        removed after being called.
        """

        def _wrapper(f):
            def g(*args, **kwargs):
                with self._lock:
                    # Check that the event wasn't removed already right
                    # before the lock
                    if event in self._events and f in self._events[event]:
                        self._remove_listener(event, f)
                    else:
                        return None
                # f may return a coroutine, so we need to return that
                # result here so that emit can schedule it
                return f(*args, **kwargs)

            self._add_event_handler(event, f, g)
            return f

        if f is None:
            return _wrapper
        else:
            return _wrapper(f)

    def _remove_listener(self, event, f):
        """Naked unprotected removal."""
        self._events[event].pop(f)

    def remove_listener(self, event, f):
        """Removes the function ``f`` from ``event``."""
        with self._lock:
            self._remove_listener(event, f)

    def remove_all_listeners(self, event=None):
        """Remove all listeners attached to ``event``.
        If ``event`` is ``None``, remove all listeners on all events.
        """
        with self._lock:
            if event is not None:
                self._events[event] = OrderedDict()
            else:
                self._events = defaultdict(OrderedDict)

    def listeners(self, event):
        """Returns a list of all listeners registered to the ``event``."""
        return list(self._events[event].keys())
