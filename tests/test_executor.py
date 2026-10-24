# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor
from threading import Event
from time import sleep
from unittest.mock import Mock

from pytest import LogCaptureFixture

from pyee.executor import ExecutorEventEmitter


class PyeeTestError(Exception):
    pass


def test_executor_emit():
    """Test that ExecutorEventEmitters can emit events."""
    with ExecutorEventEmitter() as ee:
        should_call = Mock()

        @ee.on("event")
        def event_handler():
            should_call(True)

        ee.emit("event")
        sleep(0.1)

        should_call.assert_called_once()


def test_executor_once():
    """Test that ExecutorEventEmitters also emit events for once."""
    with ExecutorEventEmitter() as ee:
        should_call = Mock()

        @ee.once("event")
        def event_handler():
            should_call(True)

        ee.emit("event")
        sleep(0.1)

        should_call.assert_called_once()


def test_executor_error():
    """Test that ExecutorEventEmitters handle errors."""
    with ExecutorEventEmitter() as ee:
        should_call = Mock()

        @ee.on("event")
        def event_handler():
            raise PyeeTestError()

        @ee.on("error")
        def handle_error(e):
            should_call(e)

        ee.emit("event")

        sleep(0.1)

        should_call.assert_called_once()


def test_executor_canceled_future(caplog: LogCaptureFixture) -> None:
    """Canceling a queued handler should not log a callback failure."""
    started = Event()
    release = Event()
    should_not_call = Mock()
    should_not_error = Mock()
    executor = ThreadPoolExecutor(max_workers=1)

    def block_worker() -> None:
        started.set()
        release.wait()

    try:
        executor.submit(block_worker)
        assert started.wait(timeout=5)

        ee = ExecutorEventEmitter(executor)
        ee.on("event", should_not_call)
        ee.on("error", should_not_error)
        assert ee.emit("event")

        executor.shutdown(wait=False, cancel_futures=True)
    finally:
        release.set()
        executor.shutdown(wait=True)

    should_not_call.assert_not_called()
    should_not_error.assert_not_called()
    assert not caplog.records
