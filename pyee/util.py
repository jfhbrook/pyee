# -*- coding: utf-8 -*-

from functools import wraps


def _wrap(left, right, error_handler):
    o_left_emit = left.emit
    o_right_emit = right.emit

    @wraps(o_left_emit)
    def wrapped_emit(event, *args, **kwargs):

        # Do it for the left side
        left_handled = left._call_handlers(event, args, kwargs)

        # Do it for the right side
        right_handled = right._call_handlers(event, args, kwargs)

        handled = left_handled or right_handled

        # Use the error handling on ``error_handler`` (should either be
        # ``left`` or ``right``)
        if not handled:
            error_handler._emit_handle_potential_error(
                event, args[0] if args else None
            )

        return handled

    def unwrap():
        left.emit = o_left_emit
        right.emit = o_right_emit

    left.emit = wrapped_emit
    left.unwrap = unwrap


def uplift(cls, underlying, *args, **kwargs):
    """A helper to create instances of an event emitter ``cls`` that inherits
    event behavior from an ``underlying`` event emitter instance.

    This is mostly helpful if you have a simple underlying event emitter
    with event handlers already attached to it, but you want to use that
    event emitter in a new context - for example, you may want to ``uplift``  a
    ``BaseEventEmitter`` supplied by a third party library into an
    ``AsyncIOEventEmitter`` so that you may register async event handlers
    in your ``asyncio`` app.

    When called, this instantiates a new instance of ``cls`` and overwrites
    the ``emit`` method on the ``old`` event emitter to also emit events on
    the new event emitter, and vice versa. In both cases, they return whether
    the ``emit`` method was handled by either emitter. Execution order prefers
    the event emitter on which ``emit`` was called. When unhandled ``error``
    events occur, the error handling behavior of the new event emitter is
    always called in both cases.

    This also adds an ``unwrap`` method to both instances, either of which will
    unwrap both ``emit`` methods when called.

    ``new_listener`` events are also called on both emitters, even though
    only one emitter actually had a listener attached to it.

    Each event emitter tracks its own internal table of handlers.
    ``remove_listener``, ``remove_all_listeners`` and ``listeners`` all
    work independently. This means you will have to remember which event
    emitter an event handler was added to!

    Note that both the new event emitter returned by ``cls`` and the
    underlying event emitter should inherit from ``BaseEventEmitter``, or at
    least implement the "sealed" interface for the undocumented
    ``_call_handlers`` method.
    """

    new = cls(*args, **kwargs)

    _wrap(new, underlying, new)
    _wrap(underlying, new, new)

    return new
