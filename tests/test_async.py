# -*- coding: utf-8 -*-

import pytest
import pytest_asyncio.plugin  # noqa

from asyncio import Future, wait_for

try:
    from asyncio.exceptions import TimeoutError
except ImportError:
    from concurrent.futures import TimeoutError

from mock import Mock

from twisted.internet.defer import ensureDeferred, succeed

from pyee import EventEmitter, AsyncIOEventEmitter, TwistedEventEmitter


class PyeeTestError(Exception):
    pass


@pytest.mark.parametrize('cls', [
    AsyncIOEventEmitter,
    EventEmitter
])
@pytest.mark.asyncio
async def test_asyncio_emit(cls, event_loop):
    """Test that asyncio-supporting event emitters can handle wrapping
    coroutines
    """

    ee = cls(loop=event_loop)

    should_call = Future(loop=event_loop)

    @ee.on('event')
    async def event_handler():
        should_call.set_result(True)

    ee.emit('event')

    result = await wait_for(should_call, 0.1)

    assert result is True


@pytest.mark.parametrize('cls', [
    AsyncIOEventEmitter,
    EventEmitter
])
@pytest.mark.asyncio
async def test_asyncio_once_emit(cls, event_loop):
    """Test that asyncio-supporting event emitters also wrap coroutines when
    using once
    """

    ee = cls(loop=event_loop)

    should_call = Future(loop=event_loop)

    @ee.once('event')
    async def event_handler():
        should_call.set_result(True)

    ee.emit('event')

    result = await wait_for(should_call, 0.1)

    assert result is True


@pytest.mark.parametrize('cls', [
    AsyncIOEventEmitter,
    EventEmitter
])
@pytest.mark.asyncio
async def test_asyncio_error(cls, event_loop):
    """Test that asyncio-supporting event emitters can handle errors when
    wrapping coroutines
    """
    ee = cls(loop=event_loop)

    should_call = Future(loop=event_loop)

    @ee.on('event')
    async def event_handler():
        raise PyeeTestError()

    @ee.on('error')
    def handle_error(exc):
        should_call.set_result(exc)

    ee.emit('event')

    result = await wait_for(should_call, 0.1)

    assert isinstance(result, PyeeTestError)


@pytest.mark.asyncio
async def test_asyncio_cancellation(event_loop):
    """Test that AsyncIOEventEmitter can handle Future cancellations"""

    cancel_me = Future(loop=event_loop)
    should_not_call = Future(loop=event_loop)

    ee = AsyncIOEventEmitter(loop=event_loop)

    @ee.on('event')
    async def event_handler():
        cancel_me.cancel()

    @ee.on('error')
    def handle_error(exc):
        should_not_call.set_result(None)

    ee.emit('event')

    try:
        await wait_for(should_not_call, 0.1)
    except TimeoutError:
        pass
    else:
        raise PyeeTestError()


@pytest.mark.asyncio
async def test_sync_error(event_loop):
    """Test that regular functions have the same error handling as coroutines
    """
    ee = AsyncIOEventEmitter(loop=event_loop)

    should_call = Future(loop=event_loop)

    @ee.on('event')
    def sync_handler():
        raise PyeeTestError()

    @ee.on('error')
    def handle_error(exc):
        should_call.set_result(exc)

    ee.emit('event')

    result = await wait_for(should_call, 0.1)

    assert isinstance(result, PyeeTestError)


@pytest.mark.parametrize('cls,kwargs', [
    (TwistedEventEmitter, dict()),
    (EventEmitter, dict(scheduler=ensureDeferred))
])
def test_twisted_emit(cls, kwargs):
    """Test that twisted-supporting event emitters can handle wrapping
    coroutines
    """
    ee = cls(**kwargs)

    should_call = Mock()

    @ee.on('event')
    async def event_handler():
        _ = await succeed('yes!')
        should_call(True)

    ee.emit('event')

    should_call.assert_called_once()


@pytest.mark.parametrize('cls,kwargs', [
    (TwistedEventEmitter, dict()),
    (EventEmitter, dict(scheduler=ensureDeferred))
])
def test_twisted_once(cls, kwargs):
    """Test that twisted-supporting event emitters also wrap coroutines for
    once
    """
    ee = cls(**kwargs)

    should_call = Mock()

    @ee.once('event')
    async def event_handler():
        _ = await succeed('yes!')
        should_call(True)

    ee.emit('event')

    should_call.assert_called_once()


def test_twisted_error():
    """Test that TwistedEventEmitters handle Failures when wrapping coroutines.
    """
    ee = TwistedEventEmitter()

    should_call = Mock()

    @ee.on('event')
    async def event_handler():
        raise PyeeTestError()

    @ee.on('failure')
    def handle_error(e):
        should_call(e)

    ee.emit('event')

    should_call.assert_called_once()
