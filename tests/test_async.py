# -*- coding: utf-8 -*-

from asyncio import Future, gather, new_event_loop, sleep
from mock import Mock
from twisted.internet.defer import ensureDeferred

from pyee import EventEmitter

class PyeeTestError(Exception):
    pass

def test_asyncio_emit():
    """Test that event_emitters can handle wrapping coroutines as used with
    asyncio.
    """
    loop = new_event_loop()
    ee = EventEmitter(loop=loop)

    should_call = Future(loop=loop)

    @ee.on('event')
    async def event_handler():
        should_call.set_result(True)

    async def create_timeout(loop=loop):
        await sleep(0.1, loop=loop)
        if not should_call.done():
            raise Exception('should_call timed out!')
            return should_call.cancel()

    timeout = create_timeout(loop=loop)

    @should_call.add_done_callback
    def _done(result):
        assert result

    ee.emit('event')

    loop.run_until_complete(gather(should_call, timeout, loop=loop))

    loop.close()


def test_asyncio_error():
    """Test that event_emitters can handle errors when wrapping coroutines as
    used with asyncio.
    """
    loop = new_event_loop()
    ee = EventEmitter(loop=loop)

    should_call = Future(loop=loop)

    @ee.on('event')
    async def event_handler():
        raise PyeeTestError()

    @ee.on('error')
    def handle_error(exc):
        should_call.set_result(exc)

    async def create_timeout(loop=loop):
        await sleep(0.1, loop=loop)
        if not should_call.done():
            raise Exception('should_call timed out!')
            return should_call.cancel()

    timeout = create_timeout(loop=loop)

    @should_call.add_done_callback
    def _done(result):
        assert isinstance(result, PyeeTestError)

    ee.emit('event')

    loop.run_until_complete(gather(should_call, timeout, loop=loop))

    loop.close()


def test_twisted_emit():
    """Test that event_emitters can handle wrapping coroutines when using
    twisted and ensureDeferred.
    """
    ee = EventEmitter(scheduler=ensureDeferred)

    should_call = Mock()

    @ee.on('event')
    async def event_handler():
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
