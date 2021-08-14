# -*- coding: utf-8 -*-

from mock import Mock
from twisted.internet.defer import inlineCallbacks
from twisted.python.failure import Failure

from pyee import TwistedEventEmitter


class PyeeTestError(Exception):
    pass


def test_propagates_failure():
    """Test that TwistedEventEmitters can propagate failures
    from twisted Deferreds
    """
    ee = TwistedEventEmitter()

    should_call = Mock()

    @ee.on("event")
    @inlineCallbacks
    def event_handler():
        yield Failure(PyeeTestError())

    @ee.on("failure")
    def handle_failure(f):
        assert isinstance(f, Failure)
        should_call(f)

    ee.emit("event")

    should_call.assert_called_once()


def test_propagates_sync_failure():
    """Test that TwistedEventEmitters can propagate failures
    from twisted Deferreds
    """
    ee = TwistedEventEmitter()

    should_call = Mock()

    @ee.on("event")
    def event_handler():
        raise PyeeTestError()

    @ee.on("failure")
    def handle_failure(f):
        assert isinstance(f, Failure)
        should_call(f)

    ee.emit("event")

    should_call.assert_called_once()


def test_propagates_exception():
    """Test that TwistedEventEmitters propagate failures as exceptions to
    the error event when no failure handler
    """

    ee = TwistedEventEmitter()

    should_call = Mock()

    @ee.on("event")
    @inlineCallbacks
    def event_handler():
        yield Failure(PyeeTestError())

    @ee.on("error")
    def handle_error(exc):
        assert isinstance(exc, Exception)
        should_call(exc)

    ee.emit("event")

    should_call.assert_called_once()
