# -*- coding: utf-8 -*-

import asyncio
from asyncio import Future, get_running_loop, sleep, wait_for
from typing import NoReturn

import pytest
import pytest_asyncio.plugin  # noqa

try:
    from asyncio.exceptions import TimeoutError  # type: ignore
except ImportError:
    from concurrent.futures import TimeoutError  # type: ignore

from pyee.asyncio import AsyncIOEventEmitter


class PyeeTestError(Exception):
    pass


@pytest.mark.asyncio
async def test_emit() -> None:
    """Test that AsyncIOEventEmitter can handle wrapping
    coroutines
    """

    ee = AsyncIOEventEmitter(loop=get_running_loop())

    should_call: Future[bool] = Future(loop=get_running_loop())

    @ee.on("event")
    async def event_handler() -> None:
        should_call.set_result(True)

    ee.emit("event")

    result = await wait_for(should_call, 0.1)

    assert result is True

    await asyncio.sleep(0)
    assert ee.complete


@pytest.mark.asyncio
async def test_once_emit() -> None:
    """Test that AsyncIOEventEmitter also wrap coroutines when
    using once
    """

    ee = AsyncIOEventEmitter(loop=get_running_loop())

    should_call: Future[bool] = Future(loop=get_running_loop())

    @ee.once("event")
    async def event_handler():
        should_call.set_result(True)

    ee.emit("event")

    result = await wait_for(should_call, 0.1)

    assert result is True


@pytest.mark.asyncio
async def test_error() -> None:
    """Test that AsyncIOEventEmitter can handle errors when
    wrapping coroutines
    """
    ee = AsyncIOEventEmitter(loop=get_running_loop())

    should_call: Future[bool] = Future(loop=get_running_loop())

    @ee.on("event")
    async def event_handler() -> NoReturn:
        raise PyeeTestError()

    @ee.on("error")
    def handle_error(exc):
        should_call.set_result(exc)

    ee.emit("event")

    result = await wait_for(should_call, 0.1)

    assert isinstance(result, PyeeTestError)


@pytest.mark.asyncio
async def test_future_canceled() -> None:
    """Test that AsyncIOEventEmitter can handle canceled Futures"""

    cancel_me: Future[bool] = Future(loop=get_running_loop())
    should_not_call: Future[None] = Future(loop=get_running_loop())

    ee = AsyncIOEventEmitter(loop=get_running_loop())

    @ee.on("event")
    async def event_handler() -> None:
        cancel_me.cancel()

    @ee.on("error")
    def handle_error(exc) -> None:
        should_not_call.set_result(None)

    ee.emit("event")

    try:
        await wait_for(should_not_call, 0.1)
    except TimeoutError:
        pass
    else:
        raise PyeeTestError()


@pytest.mark.asyncio
async def test_event_emitter_canceled() -> None:
    """Test that all running handlers in AsyncIOEventEmitter can be canceled"""

    ee = AsyncIOEventEmitter(loop=get_running_loop())

    should_not_call: Future[bool] = Future(loop=get_running_loop())

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
async def test_wait_for_complete() -> None:
    """Test waiting for all pending tasks in an AsyncIOEventEmitter to
    complete
    """

    ee = AsyncIOEventEmitter(loop=get_running_loop())

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
async def test_wait_for_complete_drains_cascading_handlers() -> None:
    """
    If a handler emits on another handler, we want those handlers to also complete
    before ee.wait_for_complete() returns.
    """

    ee = AsyncIOEventEmitter(loop=get_running_loop())

    child_started = asyncio.Event()
    release_child = asyncio.Event()
    child_done: Future[bool] = Future(loop=get_running_loop())

    @ee.on("parent")
    async def event_handler() -> None:
        # #mit the "child" event
        ee.emit("child")

    @ee.on("child")
    async def child_handler() -> None:
        # Notify the test that the child started
        child_started.set()

        # Await an asyncio event that allows the handler to complete
        await release_child.wait()

        # Mark as done
        child_done.set_result(True)

    # Since nothing is running, we should currently be "complete"
    assert ee.complete

    # Wait for all handlers to complete
    waiter = asyncio.create_task(ee.wait_for_complete())

    try:
        # Emit the parent event
        ee.emit("parent")

        # Wait for the child to start executing
        await child_started.wait()

        # process.nextTick lol
        await sleep(0)

        # The child should still be executing
        assert not waiter.done()

        # Should not yet be complete
        assert not ee.complete

        # Allow the child to complete execution
        release_child.set()

        # Now the waiter task should complete
        await waiter
    finally:
        # In an error scenario, close out blocking coroutines and wait for everything
        # manually
        release_child.set()
        ee.cancel()

        await asyncio.gather(waiter, return_exceptions=True)
        await sleep(0)

    # Child should have executed successfully
    assert child_done.done()
    assert child_done.result() is True

    # Assert the "complete" property is truthy
    assert ee.complete


@pytest.mark.asyncio
async def test_wait_for_complete_drains_async_error_handlers() -> None:
    """
    When an event raises an exception, the error handler should also complete before
    wait_for_complete returns
    """

    ee = AsyncIOEventEmitter(loop=get_running_loop())
    error_started = asyncio.Event()
    release_error = asyncio.Event()
    error_done: Future[Exception] = Future(loop=get_running_loop())

    @ee.on("event")
    async def event_handler() -> NoReturn:
        # Raise the error
        raise PyeeTestError()

    @ee.on("error")
    async def handle_error(exc: Exception) -> None:
        # Notify the test that the error handler started executing
        error_started.set()

        # Await an asyncio event that allows the handler to complete
        await release_error.wait()

        # Mark as done
        error_done.set_result(exc)

    # Since nothing is running, we should currently be "complete"
    assert ee.complete

    # Wait for all handlers, including error handlers, to complete
    waiter = asyncio.create_task(ee.wait_for_complete())

    try:
        # Emit the event
        ee.emit("event")

        # Wait for the error handler to start executing
        await error_started.wait()

        # process.nextTick lol
        await sleep(0)

        # The error handler should still be executing
        assert not waiter.done()

        # Should not yet be complete
        assert not ee.complete

        # Allow the error handler to complete execution
        release_error.set()

        # Now the waiter task should complete
        await waiter
    finally:
        # In an error scenario, close out blocking coroutines and wait for everything
        # manually
        release_error.set()
        ee.cancel()
        await asyncio.gather(waiter, return_exceptions=True)
        await sleep(0)

    # Error handler should have executed successfully
    assert error_done.done()
    assert isinstance(error_done.result(), PyeeTestError)

    # Assert the "complete" property is truthy
    assert ee.complete


@pytest.mark.asyncio
async def test_sync_error() -> None:
    """Test that regular functions have the same error handling as coroutines"""
    ee = AsyncIOEventEmitter(loop=get_running_loop())

    should_call: Future[Exception] = Future(loop=get_running_loop())

    @ee.on("event")
    def sync_handler():
        raise PyeeTestError()

    @ee.on("error")
    def handle_error(exc):
        should_call.set_result(exc)

    ee.emit("event")

    result = await wait_for(should_call, 0.1)

    assert isinstance(result, PyeeTestError)
