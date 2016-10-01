# -*- coding: utf-8 -*-

import nose.tools as nt
from asyncio import get_event_loop
from asyncio import sleep as async_sleep

from pyee import EventEmitter


def test_async_emit():
    """Test that event_emitters can handle wrapping coroutines
    """
    ee = EventEmitter()
    loop = get_event_loop()

    class SenseWasCalled():
        def __init__(self):
            self.was_called = False

        def am_calling(self):
            self.was_called = True

        def assert_was_called(self):
            nt.assert_true(self.was_called)

    sensor = SenseWasCalled()


    @ee.on('event')
    async def event_handler():
        sensor.am_calling()


    ee.emit('event')
    loop.run_until_complete(async_sleep(1))

    sensor.assert_was_called()
    

