# -*- coding: utf-8 -*-

import pytest
from mock import Mock
from time import sleep

from pyee import ExecutorEventEmitter
from pyee.namespace import NamespaceExecutorEventEmitter


class PyeeTestError(Exception):
    pass


@pytest.mark.parametrize('cls', [
    ExecutorEventEmitter,
    NamespaceExecutorEventEmitter
])
def test_executor_emit(cls):
    """Test that ExecutorEventEmitters can emit events.
    """
    with cls() as ee:
        should_call = Mock()

        @ee.on('event')
        def event_handler():
            should_call(True)

        ee.emit('event')
        sleep(0.1)

        should_call.assert_called_once()


@pytest.mark.parametrize('cls', [
    ExecutorEventEmitter,
    NamespaceExecutorEventEmitter
])
def test_executor_once(cls):
    """Test that ExecutorEventEmitters also emit events for once.
    """
    with cls() as ee:
        should_call = Mock()

        @ee.once('event')
        def event_handler():
            should_call(True)

        ee.emit('event')
        sleep(0.1)

        should_call.assert_called_once()


@pytest.mark.parametrize('cls', [
    ExecutorEventEmitter,
    NamespaceExecutorEventEmitter
])
def test_executor_error(cls):
    """Test that ExecutorEventEmitters handle errors.
    """
    with cls() as ee:
        should_call = Mock()

        @ee.on('event')
        def event_handler():
            raise PyeeTestError()

        @ee.on('error')
        def handle_error(e):
            should_call(e)

        ee.emit('event')

        sleep(0.1)

        should_call.assert_called_once()
