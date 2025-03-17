# -*- coding: utf-8 -*-

from typing import Any, Generator
from unittest.mock import Mock

from twisted.internet.defer import Deferred, inlineCallbacks, succeed
from twisted.python.failure import Failure

from pyee.twisted import TwistedEventEmitter


class PyeeTestError(Exception):
    pass


def test_emit() -> None:
    """Test that TwistedEventEmitter can handle wrapping
    coroutines
    """
    ee = TwistedEventEmitter()

    should_call = Mock()

    @ee.on("event")
    async def event_handler() -> None:
        _ = await succeed("yes!")
        should_call(True)

    ee.emit("event")

    should_call.assert_called_once()


def test_once() -> None:
    """Test that TwistedEventEmitter also wraps coroutines for
    once
    """
    ee = TwistedEventEmitter()

    should_call = Mock()

    @ee.once("event")
    async def event_handler():
        _ = await succeed("yes!")
        should_call(True)

    ee.emit("event")

    should_call.assert_called_once()


def test_error() -> None:
    """Test that TwistedEventEmitters handle Failures when wrapping coroutines."""
    ee = TwistedEventEmitter()

    should_call = Mock()

    @ee.on("event")
    async def event_handler():
        raise PyeeTestError()

    @ee.on("failure")
    def handle_error(e):
        should_call(e)

    ee.emit("event")

    should_call.assert_called_once()


def test_propagates_failure():
    """Test that TwistedEventEmitters can propagate failures
    from twisted Deferreds
    """
    ee = TwistedEventEmitter()

    should_call = Mock()

    @ee.on("event")
    @inlineCallbacks
    def event_handler() -> Generator[Deferred[object], object, None]:
        d: Deferred[Any] = Deferred()
        d.callback(Failure(PyeeTestError()))
        yield d

    @ee.on("failure")
    def handle_failure(f: Any) -> None:
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
    def event_handler() -> Generator[Deferred[object], object, None]:
        d: Deferred[Any] = Deferred()
        d.callback(Failure(PyeeTestError()))
        yield d

    @ee.on("error")
    def handle_error(exc):
        assert isinstance(exc, Exception)
        should_call(exc)

    ee.emit("event")

    should_call.assert_called_once()
