# -*- coding: utf-8 -*-

from typing import NoReturn

import pytest
import pytest_trio.plugin  # type: ignore # noqa
import trio

from pyee.trio import TrioEventEmitter


class PyeeTestError(Exception):
    pass


@pytest.mark.trio
@pytest.mark.parametrize("once", [False, True])
async def test_sync_success(once: bool) -> None:
    calls: list[int] = []
    errors: list[Exception] = []

    async with TrioEventEmitter() as ee:

        async def handle_error(exc):
            errors.append(exc)

        ee.on("error", handle_error)
        register = ee.once if once else ee.on
        register("event", calls.append)
        ee.emit("event", 42)

    assert calls == [42]
    assert errors == []


@pytest.mark.trio
async def test_once_multiple_pending_emits() -> None:
    calls = []
    errors = []
    async with TrioEventEmitter() as ee:

        @ee.once("event")
        async def event_handler():
            await trio.lowlevel.checkpoint()
            calls.append(42)

        @ee.on("error")
        async def handle_error(exc):
            errors.append(exc)

        # Both runners are queued before the first one removes the listener.
        ee.emit("event")
        ee.emit("event")

    assert calls == [42]
    assert errors == []


@pytest.mark.trio
async def test_sync_error_handler() -> None:
    error = PyeeTestError()
    errors: list[Exception] = []
    async with TrioEventEmitter() as ee:

        @ee.on("event")
        async def event_handler():
            raise error

        # One-shot also bounds any erroneous recursive error delivery.
        ee.once("error", errors.append)
        ee.emit("event")

    assert errors == [error]


@pytest.mark.trio
async def test_trio_emit() -> None:
    """Test that the trio event emitter can handle wrapping
    coroutines
    """

    async with TrioEventEmitter() as ee:
        should_call = trio.Event()

        @ee.on("event")
        async def event_handler():
            should_call.set()

        ee.emit("event")

        result = False
        with trio.move_on_after(0.1):
            await should_call.wait()
            result = True

        assert result


@pytest.mark.trio
async def test_trio_once_emit() -> None:
    """Test that trio event emitters also wrap coroutines when
    using once
    """

    async with TrioEventEmitter() as ee:
        should_call = trio.Event()

        @ee.once("event")
        async def event_handler():
            should_call.set()

        ee.emit("event")

        result = False
        with trio.move_on_after(0.1):
            await should_call.wait()
            result = True

        assert result


@pytest.mark.trio
async def test_trio_error() -> None:
    """Test that trio event emitters can handle errors when
    wrapping coroutines
    """

    async with TrioEventEmitter() as ee:
        send, rcv = trio.open_memory_channel[PyeeTestError](1)

        @ee.on("event")
        async def event_handler():
            raise PyeeTestError()

        @ee.on("error")
        async def handle_error(exc):
            async with send:
                await send.send(exc)

        ee.emit("event")

        result = None
        with trio.move_on_after(0.1):
            async with rcv:
                result = await rcv.__anext__()

        assert isinstance(result, PyeeTestError)


@pytest.mark.trio
async def test_sync_error() -> None:
    """Test that regular functions have the same error handling as coroutines"""

    async with TrioEventEmitter() as ee:
        send, rcv = trio.open_memory_channel[PyeeTestError](1)

        @ee.on("event")
        def sync_handler() -> NoReturn:
            raise PyeeTestError()

        @ee.on("error")
        async def handle_error(exc) -> None:
            async with send:
                await send.send(exc)

        ee.emit("event")

        result = None
        with trio.move_on_after(0.1):
            async with rcv:
                result = await rcv.__anext__()

        assert isinstance(result, PyeeTestError)
