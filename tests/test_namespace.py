# -*- coding: utf-8 -*-
from collections import OrderedDict

from mock import Mock
from pytest import raises

from pyee.namespace import NamespaceEventEmitter, NamespaceBlacklistException


class PyeeTestException(Exception):
    pass


def test_emit_simple():
    ee = NamespaceEventEmitter()
    call_me1 = Mock()
    call_me2 = Mock()

    # Register listener
    ee.on("event", call_me1)
    ee.on(("event",), call_me2)

    ee.emit("event", 1, 2, 3, test="so simple")
    call_me1.assert_called_once_with(1, 2, 3, test="so simple")
    call_me2.assert_called_once_with(1, 2, 3, test="so simple")

    for mock in (call_me1, call_me2):
        mock.reset_mock()

    ee.emit(("event",), 4, 5, 6, test="such ease")
    call_me1.assert_called_once_with(4, 5, 6, test="such ease")
    call_me2.assert_called_once_with(4, 5, 6, test="such ease")


def test_emit_namespace_multi_level():
    ee = NamespaceEventEmitter()
    call_me1 = Mock()
    call_me2 = Mock()
    call_me3 = Mock()

    # Register listener
    ee.on(("event",), call_me1)
    ee.on(("event", "level"), call_me2)
    ee.on(("event", "level", "type"), call_me3)

    ee.emit(("event", "level", "type"), 1, 2, 3, test="wow")

    call_me1.assert_called_once_with(1, 2, 3, test="wow")
    call_me2.assert_called_once_with(1, 2, 3, test="wow")
    call_me3.assert_called_once_with(1, 2, 3, test="wow")
    for mock in (call_me1, call_me2, call_me3):
        mock.reset_mock()

    ee.emit(("event", "level"), 4, 5, 6, test="very namespaced")
    call_me1.assert_called_once_with(4, 5, 6, test="very namespaced")
    call_me2.assert_called_once_with(4, 5, 6, test="very namespaced")
    call_me3.assert_not_called()
    for mock in (call_me1, call_me2, call_me3):
        mock.reset_mock()

    ee.emit(("event",), 7, 8, 9, test="much separation")
    call_me1.assert_called_once_with(7, 8, 9, test="much separation")
    call_me2.assert_not_called()
    call_me3.assert_not_called()


def test_emit_simple_error():
    ee = NamespaceEventEmitter()
    call_me1 = Mock()
    call_me2 = Mock()

    test_exception1 = PyeeTestException()

    with raises(PyeeTestException):
        ee.emit("error", test_exception1)

    with raises(PyeeTestException):
        ee.emit(("error",), test_exception1)

    ee.on("error", call_me1)
    ee.on(("error",), call_me2)

    # No longer raises and error instead return True indicating handled
    assert ee.emit("error", test_exception1) is True

    call_me1.assert_called_once_with(test_exception1)
    call_me2.assert_called_once_with(test_exception1)
    for mock in (call_me1, call_me2):
        mock.reset_mock()

    test_exception2 = RuntimeError()

    # No longer raises and error instead return True indicating handled
    assert ee.emit(("error",), test_exception2) is True

    call_me1.assert_called_once_with(test_exception2)
    call_me2.assert_called_once_with(test_exception2)


def test_emit_namespace_error_multi_level():
    ee = NamespaceEventEmitter()
    call_me1 = Mock()
    call_me2 = Mock()
    call_me3 = Mock()

    test_exception1 = PyeeTestException()

    with raises(PyeeTestException):
        ee.emit(("error", "level"), test_exception1)

    with raises(PyeeTestException):
        ee.emit(("error", "level", "type"), test_exception1)

    ee.on(("error", "level", "type"), call_me3)

    with raises(PyeeTestException):
        ee.emit(("error", "level"), test_exception1)

    with raises(PyeeTestException):
        ee.emit(("error",), test_exception1)

    ee.on(("error", "level"), call_me2)

    with raises(PyeeTestException):
        ee.emit(("error",), test_exception1)

    # Register listener
    ee.on(("error",), call_me1)

    test_exception2 = RuntimeError("very error")

    ee.emit(("error", "level", "type"), test_exception2)

    call_me1.assert_called_once_with(test_exception2)
    call_me2.assert_called_once_with(test_exception2)
    call_me3.assert_called_once_with(test_exception2)
    for mock in (call_me1, call_me2, call_me3):
        mock.reset_mock()

    test_exception3 = RuntimeError("oh god not")

    ee.emit(("error", "level"), test_exception3)
    call_me1.assert_called_once_with(test_exception3)
    call_me2.assert_called_once_with(test_exception3)
    call_me3.assert_not_called()
    for mock in (call_me1, call_me2, call_me3):
        mock.reset_mock()

    test_exception4 = RuntimeError("help")

    ee.emit(("error",), test_exception4)
    call_me1.assert_called_once_with(test_exception4)
    call_me2.assert_not_called()
    call_me3.assert_not_called()


def test_emit_return_specific_to_generic():
    ee = NamespaceEventEmitter()
    call_me = Mock()

    assert not ee.emit("data")
    assert not ee.emit(("data",))
    assert not ee.emit(("data", "specific"))
    assert not ee.emit(("data", "specific", "restricted"))

    ee.on(("data", "specific", "restricted"), call_me)

    assert not ee.emit("data")
    assert not ee.emit(("data",))
    assert not ee.emit(("data", "specific"))
    assert ee.emit(("data", "specific", "restricted"))

    ee.on(("data", "specific"), call_me)

    assert not ee.emit("data")
    assert not ee.emit(("data",))
    assert ee.emit(("data", "specific"))
    assert ee.emit(("data", "specific", "restricted"))

    ee.on(("data",), call_me)

    assert ee.emit("data")
    assert ee.emit(("data",))
    assert ee.emit(("data", "specific"))
    assert ee.emit(("data", "specific", "restricted"))


def test_emit_return_generic_to_specific():
    ee = NamespaceEventEmitter()
    call_me = Mock()

    assert not ee.emit("data")
    assert not ee.emit(("data",))
    assert not ee.emit(("data", "specific"))
    assert not ee.emit(("data", "specific", "restricted"))

    ee.on("data", call_me)

    assert ee.emit("data")
    assert ee.emit(("data",))
    assert ee.emit(("data", "specific"))
    assert ee.emit(("data", "specific", "restricted"))


def test_new_listener_event():
    ee = NamespaceEventEmitter()
    call_me = Mock()

    with raises(NamespaceBlacklistException):
        ee.on(("new_listener", "can't do that"), call_me)

    ee.on("new_listener", call_me)

    # Should fire new_listener event
    @ee.on("event")
    def event_handler(data):
        pass

    call_me.assert_called_once_with(("event",), event_handler)
    call_me.reset_mock()

    @ee.on(("event",))
    def event_handler(data):
        pass

    call_me.assert_called_once_with(("event",), event_handler)
    call_me.reset_mock()

    @ee.on(("event", "namespace"))
    def event_handler(data):
        pass

    call_me.assert_called_once_with(("event", "namespace"), event_handler)


def test_listener_removal():
    ee = NamespaceEventEmitter()

    # Some functions to pass to the EE
    def first():
        return 1

    ee.on(("event", "test"), first)

    @ee.on(("event", "test"))
    def second():
        return 2

    @ee.on(("event", "test"))
    def third():
        return 3

    def fourth():
        return 4

    ee.on(("event", "test"), fourth)

    assert ee._events[("event", "test")] == OrderedDict(
        [(first, first), (second, second), (third, third), (fourth, fourth)]
    )

    ee.remove_listener(("event", "test"), second)

    assert ee._events[("event", "test")] == OrderedDict(
        [(first, first), (third, third), (fourth, fourth)]
    )

    ee.remove_listener(("event", "test"), first)
    assert ee._events[("event", "test")] == OrderedDict(
        [(third, third), (fourth, fourth)]
    )

    ee.remove_all_listeners(("event", "test"))
    assert ee._events[("event", "test")] == OrderedDict()
