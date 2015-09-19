# -*- coding: utf-8 -*-

import nose.tools as nt
from pyee import Event_emitter, EventEmitter


class ItWorkedException(Exception):
    """An exception, used to prove that an event handler fired.
    Kinda hack-y, I know.
    """
    pass

def test_emit():
    """Test that event_emitters fire properly.
    """
    ee = Event_emitter()

    # Used in a decorator style
    @ee.on('event')
    def event_handler(data, **kwargs):
        nt.assert_equals(data, 'emitter is emitted!')
        # Raise exception to prove it fired.
        if (kwargs['error']):
            raise ItWorkedException

    # Making sure data is passed propers
    ee.emit('event', 'emitter is emitted!', error=False)

    # Some nose bullshit to check for the firings. 
    # "Hides" other exceptions.
    with nt.assert_raises(ItWorkedException) as it_worked:
        ee.emit('event', 'emitter is emitted!', error=True)

def test_emit_error():
    ee = EventEmitter()
    
    with nt.assert_raises(Exception):
        ee.emit('error')

    @ee.on('error')
    def onError():
        pass
        
    # No longer raises and error instead return True indicating handled
    nt.assert_true(ee.emit('error'))

def test_emit_return():
    ee = EventEmitter()
    
    # make sure emitting without a callback returns False
    nt.assert_false(ee.emit('data'))

    # add a callback
    ee.on('data')(lambda: None)

    # should return True now
    nt.assert_true(ee.emit('data'))

def test_new_listener_event():
    """Test the 'new_listener' event.
    """

    ee = Event_emitter()

    @ee.on('new_listener')
    def new_listener_handler(event, fxn):
        raise ItWorkedException

    with nt.assert_raises(ItWorkedException) as it_worked:
        @ee.on('event')
        def event_handler(data):
            pass

    
def test_listener_removal():
    """Tests that we can remove listeners (as appropriate).
    """

    ee = Event_emitter()


    #Some functions to pass to the EE
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

    nt.assert_equal(ee._events['event'], [first, second, third, fourth])

    # uses the function itself to find/remove listener
    ee.remove_listener('event', second)
    nt.assert_equal(ee._events['event'], [first, third, fourth])

    # uses the function itself to find/remove listener
    ee.remove_listener('event', first)
    nt.assert_equal(ee._events['event'], [third, fourth])

    # Remove ALL listeners!
    ee.remove_all_listeners('event')
    nt.assert_equal(ee._events['event'], [])

def test_once():
    """Test that `once()` method works propers.
    """

    # very similar to "test_emit" but also makes sure that the event
    # gets removed afterwards

    ee = Event_emitter()

    def once_handler(data, error=None):
        nt.assert_equals(data, 'emitter is emitted!')
        if (error):
            raise ItWorkedException

    #Tests to make sure that after event is emitted that it's gone.
    ee.once('event', once_handler)
    ee.emit('event', 'emitter is emitted!')
    nt.assert_equal(ee._events['event'], [])

    #Tests to make sure callback fires. "Hides" other exceptions.
    with nt.assert_raises(ItWorkedException) as it_worked:
        ee.once('event', once_handler)
        ee.emit('event', 'emitter is emitted!', True)

def test_listeners():
    """Test that `listeners()` gives you access to the listeners array.
    """
    
    ee = Event_emitter()
    @ee.on('event')
    def event_handler():
        pass

    def raiser():
        raise ItWorkedException

    l = ee.listeners('event')
    l[0] = raiser

    with nt.assert_raises(ItWorkedException) as it_worked:
        ee.emit('event')

def test_properties_preserved():
    """Test that the properties of decorated functions are preserved.
    """
    ee = EventEmitter()

    @ee.on('always')
    def always_event_handler():
        """An event handler."""
        raise ItWorkedException

    @ee.once('once')
    def once_event_handler():
        """Another event handler."""
        raise ItWorkedException

    nt.assert_equal(always_event_handler.__doc__, 'An event handler.')
    nt.assert_equal(once_event_handler.__doc__, 'Another event handler.')

    with nt.assert_raises(ItWorkedException) as it_worked:
        # Call the event handler directly.
        always_event_handler()

    with nt.assert_raises(ItWorkedException):
        # Call the event handler directly.
        once_event_handler()

    with nt.assert_raises(ItWorkedException):
        # Assert that it does not matter, that the handler has already been
        # called directly.
        ee.emit('once')
