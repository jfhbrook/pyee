# -*- coding: utf-8 -*-
import nose.tools as nt
from asyncio import Future, gather, get_event_loop, sleep

from pyee import EventEmitter


def test_async_emit():
    """Test that event_emitters can handle wrapping coroutines
    """
    loop = get_event_loop()
    ee = EventEmitter(loop=loop)

    future = Future()

    @ee.on('event')
    async def event_handler():
        future.set_result(True)

    async def create_timeout(loop=loop):
        await sleep(1, loop=loop)
        future.cancel()

    timeout = create_timeout(loop=loop)

    @future.add_done_callback
    def _done(result):
        nt.assert_true(result)

    ee.emit('event')

    loop.run_until_complete(gather(future, timeout))
