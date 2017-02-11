# -*- coding: utf-8 -*-

from inspect import getmro

from mock import Mock
from pytest import raises

from pyee import EventEmitter

class PyeeTestException(Exception):
    pass

def test_emit_sync():
    """Basic synchronous emission works"""

    call_me = Mock()
    ee = EventEmitter()

    @ee.on('event')
    def event_handler(data, **kwargs):
        call_me()
        assert data == 'emitter is emitted!'

    # Making sure data is passed propers
    ee.emit('event', 'emitter is emitted!', error=False)

    call_me.assert_called_once()


def test_emit_error():
    """Errors raise with no event handler, otherwise emit on handler"""

    call_me = Mock()
    ee = EventEmitter()

    test_exception = PyeeTestException('lololol')

    with raises(PyeeTestException) as exc_info:
        ee.emit('error', test_exception)

    @ee.on('error')
    def on_error(exc):
        call_me()

    # No longer raises and error instead return True indicating handled
    assert ee.emit('error', test_exception)
    call_me.assert_called_once()


def test_emit_return():
    """Emit returns True when handlers are registered on an event, and false
    otherwise.
    """

    call_me = Mock()
    ee = EventEmitter()

    # make sure emitting without a callback returns False
    assert not ee.emit('data')

    # add a callback
    ee.on('data')(call_me)

    # should return True now
    assert ee.emit('data')


def test_new_listener_event():
    """The 'new_listener' event fires whenever a new listerner is added."""

    call_me = Mock()
    ee = EventEmitter()

    ee.on('new_listener', call_me)

    # Should fire new_listener event
    @ee.on('event')
    def event_handler(data):
        pass

    call_me.assert_called_once()


def test_listener_removal():
    """Removing listeners removes the correct listener from an event."""

    ee = EventEmitter()

    # Some functions to pass to the EE
    def first():
        return 1

    ee.on('event', first)

    @ee.on('event')
    def second():
        return 2

    @ee.on('event')
    def third():
        return 3

    def fourth():
        return 4

    ee.on('event', fourth)

    assert ee._events['event'] == [first, second, third, fourth]

    ee.remove_listener('event', second)

    assert ee._events['event'] == [first, third, fourth]

    ee.remove_listener('event', first)
    assert ee._events['event'] == [third, fourth]

    ee.remove_all_listeners('event')
    assert ee._events['event'] == []


def test_listener_removal_on_emit():
    """Test that a listener removed during an emit is called inside the current
    emit cycle.
    """

    call_me = Mock()
    ee = EventEmitter()

    def should_remove():
        ee.remove_listener('remove', call_me)

    ee.on('remove', should_remove)
    ee.on('remove', call_me)

    ee.emit('remove')

    call_me.assert_called_once()

    call_me.reset_mock()

    # Also test with the listeners added in the opposite order
    ee = EventEmitter()
    ee.on('remove', call_me)
    ee.on('remove', should_remove)

    ee.emit('remove')

    call_me.assert_called_once()


def test_once():
    """Test that `once()` method works propers.
    """

    # very similar to "test_emit" but also makes sure that the event
    # gets removed afterwards

    call_me = Mock()
    ee = EventEmitter()

    def once_handler(data):
        assert data == 'emitter is emitted!'
        call_me()

    # Tests to make sure that after event is emitted that it's gone.
    callback_fn = ee.once('event', once_handler)

    # assert ee._events['event'] == [callback_fn]

    ee.emit('event', 'emitter is emitted!')

    call_me.assert_called_once()

    assert ee._events['event'] == []


def test_listeners():
    """`listeners()` gives you access to the listeners array."""

    call_me = Mock()
    ee = EventEmitter()

    @ee.on('event')
    def event_handler():
        pass

    listeners = ee.listeners('event')

    assert listeners[0] == event_handler

    # Overwrite listener
    listeners[0] = call_me

    ee.emit('event')

    call_me.assert_called_once()


def test_properties_preserved():
    """Test that the properties of decorated functions are preserved."""

    call_me = Mock()
    call_me_also = Mock()
    ee = EventEmitter()

    @ee.on('always')
    def always_event_handler():
        """An event handler."""
        call_me()

    @ee.once('once')
    def once_event_handler():
        """Another event handler."""
        call_me_also()

    assert always_event_handler.__doc__ == 'An event handler.'
    assert once_event_handler.__doc__ == 'Another event handler.'

    always_event_handler()
    call_me.assert_called_once()

    once_event_handler()
    call_me_also.assert_called_once()

    call_me_also.reset_mock()

    # Calling the event handler directly doesn't clear the handler
    ee.emit('once')
    call_me_also.assert_called_once()


def test_inheritance():
    """Test that inheritance is preserved from object"""
    assert object in getmro(EventEmitter)

    class example(EventEmitter):
        def __init__(self):
            super(example, self).__init__()

    assert EventEmitter in getmro(example)
    assert object in getmro(example)

def test_multiple_inheritance():
    """Test that inheritance is preserved along a lengthy MRO"""
    class example(EventEmitter):
        def __init__(self):
            super(example, self).__init__()

    class _example(example):
        def __init__(self):
            super(_example, self).__init__()

    class example2(_example):
        def __init__(self):
            super(example2, self).__init__()

    class _example2(_example):
        def __init__(self):
            super(_example2, self).__init__()

    a = _example2()
