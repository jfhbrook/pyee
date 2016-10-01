# -*- coding: utf-8 -*-
import nose.tools as nt
from asyncio import Future, gather, new_event_loop, sleep

from pyee import EventEmitter


def test_async_emit():
    """Test that event_emitters can handle wrapping coroutines
    """
    loop = new_event_loop()
    ee = EventEmitter(loop=loop)

    should_call = Future(loop=loop)

    @ee.on('event')
    async def event_handler():
        should_call.set_result(True)

    async def create_timeout(loop=loop):
        await sleep(1, loop=loop)
        if not should_call.done():
            raise Exception('should_call timed out!')
            return should_call.cancel()

    timeout = create_timeout(loop=loop)

    @should_call.add_done_callback
    def _done(result):
        nt.assert_true(result)

    ee.emit('event')

    loop.run_until_complete(gather(should_call, timeout, loop=loop))

    loop.close()
