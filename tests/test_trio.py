# -*- coding: utf-8 -*-

import pytest
import pytest_trio.plugin  # noqa
import trio

from pyee import TrioEventEmitter


class PyeeTestError(Exception):
    pass


@pytest.mark.trio
async def test_trio_emit():
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
async def test_trio_once_emit():
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
async def test_trio_error():
    """Test that trio event emitters can handle errors when
    wrapping coroutines
    """

    async with TrioEventEmitter() as ee:
        send, rcv = trio.open_memory_channel(1)

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
async def test_sync_error(event_loop):
    """Test that regular functions have the same error handling as coroutines"""

    async with TrioEventEmitter() as ee:
        send, rcv = trio.open_memory_channel(1)

        @ee.on("event")
        def sync_handler():
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
