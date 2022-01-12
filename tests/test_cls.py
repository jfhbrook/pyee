# -*- coding: utf-8 -*-
from mock import Mock
import pytest

from pyee import EventEmitter
from pyee.cls import evented, on


@evented
class EventedFixture:
    def __init__(self):
        self.call_me = Mock()

    @on("event")
    def event_handler(self, *args, **kwargs):
        self.call_me(self, *args, **kwargs)


_custom_event_emitter = EventEmitter()


@evented
class CustomEmitterFixture:
    def __init__(self):
        self.call_me = Mock()
        self.event_emitter = _custom_event_emitter

    @on("event")
    def event_handler(self, *args, **kwargs):
        self.call_me(self, *args, **kwargs)


class InheritedFixture(EventedFixture):
    pass


@pytest.mark.parametrize(
    "cls", [EventedFixture, CustomEmitterFixture, InheritedFixture]
)
def test_evented_decorator(cls):
    inst = cls()

    inst.event_emitter.emit("event", "emitter is emitted!")

    inst.call_me.assert_called_once_with(inst, "emitter is emitted!")

    _custom_event_emitter.remove_all_listeners()
