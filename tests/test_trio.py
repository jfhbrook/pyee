from typing import NoReturn

import pytest
import pytest_trio.plugin  # type: ignore # noqa
import trio

from pyee.base import PyeeError
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


@pytest.mark.trio
@pytest.mark.parametrize("failure", ["none", "body", "handler"])
@pytest.mark.parametrize("direct", [True, False])
async def test_owned_nursery_cleared_after_exit(failure: str, direct: bool) -> None:
    ee = TrioEventEmitter()

    def handler() -> None:
        if failure == "handler":
            raise PyeeTestError("handler failed")

    ee.on("event", handler)
    try:
        async with ee.context() if direct else ee:
            ee.emit("event")
            if failure == "body":
                raise PyeeTestError("body failed")
    except BaseExceptionGroup as exc:
        assert failure != "none"
        assert any(isinstance(e, PyeeTestError) for e in exc.exceptions)
    else:
        assert failure == "none"

    assert ee._nursery is None
    if not direct:
        assert ee._context is None
        assert ee._manager is None
    with pytest.raises(PyeeError, match="Uninitialized trio nursery"):
        ee.emit("event")


@pytest.mark.trio
async def test_direct_context_does_not_close_borrowed_nursery() -> None:
    calls: list[int] = []
    async with trio.open_nursery() as nursery:
        ee = TrioEventEmitter(nursery=nursery)
        ee.on("event", calls.append)
        async with ee.context():
            ee.emit("event", 1)
        assert ee._nursery is nursery
        ee.emit("event", 2)
    assert sorted(calls) == [1, 2]


@pytest.mark.trio
@pytest.mark.parametrize("direct", [True, False])
async def test_owned_nursery_cleared_after_cancellation(direct: bool) -> None:
    ee = TrioEventEmitter()
    with trio.move_on_after(0) as scope:
        async with ee.context() if direct else ee:
            scope.cancel()
            await trio.lowlevel.checkpoint()
    assert scope.cancelled_caught
    assert ee._nursery is None
    if not direct:
        assert ee._context is None
        assert ee._manager is None


@pytest.mark.trio
async def test_emit_after_owned_context_uses_uninitialized_error() -> None:
    ee = TrioEventEmitter()
    ee.on("event", lambda: None)
    async with ee.context():
        ee.emit("event")
    with pytest.raises(PyeeError, match="Uninitialized trio nursery"):
        ee.emit("event")
