# -*- coding: utf-8 -*-

import pytest
import pytest_asyncio.plugin

from asyncio import Future, gather, new_event_loop, sleep
from mock import Mock
from twisted.internet.defer import ensureDeferred, succeed

from pyee import EventEmitter


class PyeeTestError(Exception):
    pass


@pytest.mark.asyncio
async def test_asyncio_emit(event_loop):
    """Test that event_emitters can handle wrapping coroutines as used with
    asyncio.
    """

    ee = EventEmitter(loop=event_loop)

    should_call = Future(loop=event_loop)

    @ee.on('event')
    async def event_handler():
        should_call.set_result(True)

    async def create_timeout(loop=event_loop):
        await sleep(0.1, loop=event_loop)
        if not should_call.done():
            should_call.cancel()
            raise Exception('should_call timed out!')

    timeout = create_timeout(loop=event_loop)

    ee.emit('event')

    result = await should_call

    assert result == True


@pytest.mark.asyncio
async def test_asyncio_once_emit(event_loop):
    """Test that event_emitters also wrap coroutines when using once
    """

    ee = EventEmitter(loop=event_loop)

    should_call = Future(loop=event_loop)

    @ee.once('event')
    async def event_handler():
        should_call.set_result(True)

    async def create_timeout(loop=event_loop):
        await sleep(0.1, loop=event_loop)
        if not should_call.done():
            should_call.cancel()
            raise Exception('should_call timed out!')

    timeout = create_timeout(loop=event_loop)

    ee.emit('event')

    result = await should_call

    assert result == True


@pytest.mark.asyncio
async def test_asyncio_error(event_loop):
    """Test that event_emitters can handle errors when wrapping coroutines as
    used with asyncio.
    """
    ee = EventEmitter(loop=event_loop)

    should_call = Future(loop=event_loop)

    @ee.on('event')
    async def event_handler():
        raise PyeeTestError()

    @ee.on('error')
    def handle_error(exc):
        assert isinstance(exc, PyeeTestError)
        should_call.set_result(exc)

    async def create_timeout(loop=event_loop):
        await sleep(0.1, loop=event_loop)
        if not should_call.done():
            raise Exception('should_call timed out!')
            return should_call.cancel()

    timeout = create_timeout(loop=event_loop)

    ee.emit('event')

    result = await should_call

    assert isinstance(result, PyeeTestError)


def test_twisted_emit():
    """Test that event_emitters can handle wrapping coroutines when using
    twisted and ensureDeferred.
    """
    ee = EventEmitter(scheduler=ensureDeferred)

    should_call = Mock()

    @ee.on('event')
    async def event_handler():
        _ = await succeed('yes!')
        should_call(True)

    ee.emit('event')

    should_call.assert_called_once()


def test_twisted_once():
    """Test that event_emitters also wrap coroutines for once when using
    twisted and ensureDeferred.
    """
    ee = EventEmitter(scheduler=ensureDeferred)

    should_call = Mock()

    @ee.once('event')
    async def event_handler():
        _ = await succeed('yes!')
        should_call(True)

    ee.emit('event')

    should_call.assert_called_once()


def test_twisted_error():
    """Test that event_emitters can handle wrapping coroutines when using
    twisted and ensureDeferred.
    """
    ee = EventEmitter(scheduler=ensureDeferred)

    should_call = Mock()

    @ee.on('event')
    async def event_handler():
        raise PyeeTestError()

    @ee.on('error')
    def handle_error(e):
        should_call(e)

    ee.emit('event')

    should_call.assert_called_once()
