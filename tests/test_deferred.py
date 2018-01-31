# -*- coding: utf-8 -*-

import pytest

from mock import Mock
from twisted.internet.defer import inlineCallbacks, succeed

from pyee import EventEmitter


class PyeeTestError(Exception):
    pass


def test_propagates_error():
    """Test that event_emitters can propagate errors
    from twisted Deferreds
    """
    ee = EventEmitter()

    should_call = Mock()

    @ee.on('event')
    @inlineCallbacks
    def event_handler():
        raise PyeeTestError()

    @ee.on('error')
    def handle_error(e):
        should_call(e)

    ee.emit('event')

    should_call.assert_called_once()
