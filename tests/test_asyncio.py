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
    """Handlers emitted by a running handler are included in the barrier."""
    ee = AsyncIOEventEmitter(loop=get_running_loop())
    child_started = asyncio.Event()
    release_child = asyncio.Event()
    child_done: Future[bool] = Future(loop=get_running_loop())

    @ee.on("event")
    async def event_handler() -> None:
        ee.emit("child")

    @ee.on("child")
    async def child_handler() -> None:
        child_started.set()
        await release_child.wait()
        child_done.set_result(True)

    waiter = asyncio.create_task(ee.wait_for_complete())
    try:
        ee.emit("event")
        await child_started.wait()
        await sleep(0)

        assert not waiter.done()

        release_child.set()
        await waiter
    finally:
        release_child.set()
        ee.cancel()
        await asyncio.gather(waiter, return_exceptions=True)
        await sleep(0)

    assert child_done.done()
    assert child_done.result() is True
    assert ee.complete


@pytest.mark.asyncio
async def test_wait_for_complete_drains_async_error_handlers() -> None:
    """Async error handlers emitted from completion callbacks are awaited."""
    ee = AsyncIOEventEmitter(loop=get_running_loop())
    error_started = asyncio.Event()
    release_error = asyncio.Event()
    error_done: Future[Exception] = Future(loop=get_running_loop())

    @ee.on("event")
    async def event_handler() -> NoReturn:
        raise PyeeTestError()

    @ee.on("error")
    async def handle_error(exc: Exception) -> None:
        error_started.set()
        await release_error.wait()
        error_done.set_result(exc)

    waiter = asyncio.create_task(ee.wait_for_complete())
    try:
        ee.emit("event")
        await error_started.wait()
        await sleep(0)

        assert not waiter.done()

        release_error.set()
        await waiter
    finally:
        release_error.set()
        ee.cancel()
        await asyncio.gather(waiter, return_exceptions=True)
        await sleep(0)

    assert error_done.done()
    assert isinstance(error_done.result(), PyeeTestError)
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
