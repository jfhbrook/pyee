# -*- coding: utf-8 -*-

import asyncio
from asyncio import Future, sleep, wait_for

import pytest
import pytest_asyncio.plugin  # noqa

try:
    from asyncio.exceptions import TimeoutError  # type: ignore
except ImportError:
    from concurrent.futures import TimeoutError  # type: ignore

from unittest.mock import Mock

from twisted.internet.defer import succeed

from pyee.asyncio import AsyncIOEventEmitter
from pyee.twisted import TwistedEventEmitter


class PyeeTestError(Exception):
    pass


@pytest.mark.asyncio
async def test_asyncio_emit(event_loop) -> None:
    """Test that AsyncIOEventEmitter can handle wrapping
    coroutines
    """

    ee = AsyncIOEventEmitter(loop=event_loop)

    should_call = Future(loop=event_loop)

    @ee.on("event")
    async def event_handler():
        should_call.set_result(True)

    ee.emit("event")

    result = await wait_for(should_call, 0.1)

    assert result is True

    await asyncio.sleep(0)
    assert ee.complete


@pytest.mark.asyncio
async def test_asyncio_once_emit(event_loop) -> None:
    """Test that AsyncIOEventEmitter also wrap coroutines when
    using once
    """

    ee = AsyncIOEventEmitter(loop=event_loop)

    should_call = Future(loop=event_loop)

    @ee.once("event")
    async def event_handler():
        should_call.set_result(True)

    ee.emit("event")

    result = await wait_for(should_call, 0.1)

    assert result is True


@pytest.mark.asyncio
async def test_asyncio_error(event_loop) -> None:
    """Test that AsyncIOEventEmitter can handle errors when
    wrapping coroutines
    """
    ee = AsyncIOEventEmitter(loop=event_loop)

    should_call = Future(loop=event_loop)

    @ee.on("event")
    async def event_handler():
        raise PyeeTestError()

    @ee.on("error")
    def handle_error(exc):
        should_call.set_result(exc)

    ee.emit("event")

    result = await wait_for(should_call, 0.1)

    assert isinstance(result, PyeeTestError)


@pytest.mark.asyncio
async def test_asyncio_future_canceled(event_loop) -> None:
    """Test that AsyncIOEventEmitter can handle canceled Futures"""

    cancel_me = Future(loop=event_loop)
    should_not_call = Future(loop=event_loop)

    ee = AsyncIOEventEmitter(loop=event_loop)

    @ee.on("event")
    async def event_handler():
        cancel_me.cancel()

    @ee.on("error")
    def handle_error(exc):
        should_not_call.set_result(None)

    ee.emit("event")

    try:
        await wait_for(should_not_call, 0.1)
    except TimeoutError:
        pass
    else:
        raise PyeeTestError()


@pytest.mark.asyncio
async def test_asyncio_event_emitter_canceled(event_loop) -> None:
    """Test that all running handlers in AsyncIOEventEmitter can be canceled"""

    ee = AsyncIOEventEmitter(loop=event_loop)

    should_not_call = Future(loop=event_loop)

    @ee.on("event")
    async def event_handler():
        await sleep(1)
        should_not_call.set_result(True)

    ee.emit("event")

    await sleep(0)

    # event_handler should still be running
    assert not ee.complete

    # cancel all pending tasks, including event_handler
    ee.cancel()

    await sleep(0)

    # event_handler should be canceled
    assert ee.complete


@pytest.mark.asyncio
async def test_asyncio_wait_for_complete(event_loop) -> None:
    """Test waiting for all pending tasks in an AsyncIOEventEmitter to
    complete
    """

    ee = AsyncIOEventEmitter(loop=event_loop)

    @ee.on("event")
    async def event_handler():
        await sleep(0.1)

    ee.emit("event")

    await sleep(0)

    # event_handler should still be running
    assert not ee.complete

    # wait for event_handler to complete execution
    await ee.wait_for_complete()

    # event_handler should have finished execution
    assert ee.complete


@pytest.mark.asyncio
async def test_sync_error(event_loop) -> None:
    """Test that regular functions have the same error handling as coroutines"""
    ee = AsyncIOEventEmitter(loop=event_loop)

    should_call = Future(loop=event_loop)

    @ee.on("event")
    def sync_handler():
        raise PyeeTestError()

    @ee.on("error")
    def handle_error(exc):
        should_call.set_result(exc)

    ee.emit("event")

    result = await wait_for(should_call, 0.1)

    assert isinstance(result, PyeeTestError)


def test_twisted_emit() -> None:
    """Test that TwistedEventEmitter can handle wrapping
    coroutines
    """
    ee = TwistedEventEmitter()

    should_call = Mock()

    @ee.on("event")
    async def event_handler():
        _ = await succeed("yes!")
        should_call(True)

    ee.emit("event")

    should_call.assert_called_once()


def test_twisted_once() -> None:
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


def test_twisted_error() -> None:
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
