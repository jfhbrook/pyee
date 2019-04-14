# -*- coding: utf-8 -*-

from collections import OrderedDict


def evolve(cls, underlying, *args, **kwargs):
    """A helper to create instances of ``cls`` that inherit event behavior
    from an ``underlying`` instance.

    When called, this instantiates a new instance of ``cls`` and then copies
    all the handlers on ``underlying`` to that new instance, before returning
    it. Afterwards, any modifications made to the underlying event emitter
    and the new "evolved" event emitter are not shared.

    Note that ``cls`` must be able to directly handle all of the same kinds
    of handlers as ``underlying``. For example, you could evolve a
    ``BaseEventEmitter`` into an ``AsyncIOEventEmitter``, but evolving a
    ``AsyncIOEventEmitter`` with asyncio coroutine handlers into a
    ``TwistedEventEmitter``, calls to those handlers from the evolved event
    emitter will fail as ``TwistedEventEmitter`` only knows how to run
    Deferreds, not Futures/Tasks.
    """
    new = cls(*args, **kwargs)

    for event_name, handlers in underlying._events.items():
        new._events[event_name] = OrderedDict([
            (k, v)
            for k, v in handlers.items()
        ])

    return new
