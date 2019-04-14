# -*- coding: utf-8 -*-

from collections import OrderedDict


def evolve(cls, underlying, *args, **kwargs):
    """A helper to create instances of an event emitter ``cls`` that inherit
    event behavior from an ``underlying`` event emitter instance.

    When called, this instantiates a new instance of ``cls`` and then copies
    all the handlers on ``underlying`` to that new instance, before returning
    it. Afterwards, any modifications made to the underlying event emitter
    and the new "evolved" event emitter are not shared.

    This is mostly helpful if you have a simple underlying event emitter
    with event handlers already attached to it, but you want to use that
    event emitter in a new context - for example, using a ``BaseEventEmitter``
    supplied by a third party library into an ``AsyncIOEventEmitter`` for
    use in your ``asyncio`` app.

    Note that ``cls`` must be able to directly handle all of the same kinds
    of handlers as ``underlying``. For example, when evolving a
    ``AsyncIOEventEmitter`` with asyncio coroutine handlers into a
    ``TwistedEventEmitter``, the ``evolve`` call will successfully return
    a ``TwistedEventEmitter`` but calls to those asyncio coroutine handlers
    from the evolved event emitter will fail as ``TwistedEventEmitter`` only
    knows how to run Deferreds, not Futures/Tasks. In this case, you're
    probably "stuck" with ``asyncio``.
    """
    new = cls(*args, **kwargs)

    for event_name, handlers in underlying._events.items():
        new._events[event_name] = OrderedDict([
            (k, v)
            for k, v in handlers.items()
        ])

    return new
