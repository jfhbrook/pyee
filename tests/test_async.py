# -*- coding: utf-8 -*-

import pytest
import pytest_asyncio.plugin

from asyncio import Future, gather, new_event_loop, wait_for
from mock import Mock
from twisted.internet.defer import ensureDeferred, succeed

from pyee import EventEmitter, AsyncIOEventEmitter, TwistedEventEmitter


class PyeeTestError(Exception):
    pass


@pytest.mark.asyncio
async def test_asyncio_emit(event_loop):
    """Test that EventEmitters can handle wrapping coroutines as used with
    asyncio.
    """

    ee = AsyncIOEventEmitter(loop=event_loop)

    should_call = Future(loop=event_loop)

    @ee.on('event')
    async def event_handler():
        should_call.set_result(True)

    ee.emit('event')

    result = await wait_for(should_call, 0.1)

    assert result == True


@pytest.mark.asyncio
async def test_asyncio_once_emit(event_loop):
    """Test that EventEmitters also wrap coroutines when using once
    """

    ee = AsyncIOEventEmitter(loop=event_loop)

    should_call = Future(loop=event_loop)

    @ee.once('event')
    async def event_handler():
        should_call.set_result(True)

    ee.emit('event')

    result = await wait_for(should_call, 0.1)

    assert result == True


@pytest.mark.asyncio
async def test_asyncio_error(event_loop):
    """Test that EventEmitters can handle errors when wrapping coroutines as
    used with asyncio.
    """
    ee = AsyncIOEventEmitter(loop=event_loop)

    should_call = Future(loop=event_loop)

    @ee.on('event')
    async def event_handler():
        raise PyeeTestError()

    @ee.on('error')
    def handle_error(exc):
        assert isinstance(exc, PyeeTestError)
        should_call.set_result(exc)

    ee.emit('event')

    result = await wait_for(should_call, 0.1)

    assert isinstance(result, PyeeTestError)


def test_twisted_emit():
    """Test that TwistedEventEmitters can handle wrapping coroutines.
    """
    ee = TwistedEventEmitter()

    should_call = Mock()

    @ee.on('event')
    async def event_handler():
        _ = await succeed('yes!')
        should_call(True)

    ee.emit('event')

    should_call.assert_called_once()


def test_twisted_once():
    """Test that TwistedEventEmitters also wrap coroutines for once.
    """
    ee = TwistedEventEmitter()

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
