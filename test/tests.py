import nose.tools as nt
from pyee import EventEmitter

# An exception, used to prove that an event handler fired.
# Kinda hack-y, I know.
class ItWorkedException(Exception):
    pass

def test_emit():
    """
    Test to show that event_emitters fire properly.
    """
    ee = EventEmitter()

    #Used in a decorator style.
    @ee.on('event')
    def event_handler(data, **kwargs):
        nt.assert_equals(data, 'emitter is emitted!')
        # Raise exception to prove it fired.
        if (kwargs['error']):
            raise ItWorkedException

    #Making sure data is passed propers.
    ee.emit('event', 'emitter is emitted!', error=False)

    # Some nose bullshit to check for the firings. "Hides" other exceptions.
    with nt.assert_raises(ItWorkedException) as it_worked:
        ee.emit('event', 'emitter is emitted!', error=True)

def test_new_listener_event():
    """
    test for the 'new_listener' event
    """

    ee = EventEmitter()

    @ee.on('new_listener')
    def new_listener_handler():
        raise ItWorkedException

    with nt.assert_raises(ItWorkedException) as it_worked:
        @ee.on('event')
        def event_handler(data):
            pass

    
def test_listener_removal():
    """
    tests to make sure we can remove listeners as appropriate.
    """

    ee = EventEmitter()


    #Some functions to pass to the EE
    def first():
        return 1

    def second():
        return 2

    def third():
        return 3

    #If you want un-closed functions, you unfortunately have to
    #call ee without using decorator styles.
    ee.on('event', first)
    ee.on('event', second)
    ee.on('event', third)

    nt.assert_equal(ee._events['event'], [first, second, third])

    #uses the function itself to find/remove listener
    ee.remove_listener('event', second)
    nt.assert_equal(ee._events['event'], [first, third])

    #remove ALL the listeners!
    ee.remove_all_listeners('event')
    nt.assert_equal(ee._events['event'], [])

def test_once():
    """
    Test to show that the "once" method works propers.
    """

    # very similar to "test_emit" but also makes sure that the event
    # gets removed afterwards

    ee = EventEmitter()

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
    """
    Test to make sure that the listeners method gives you access to the listeners array.
    """
    ee = EventEmitter()
    @ee.on('event')
    def event_handler():
        pass

    def raiser():
        raise ItWorkedException

    l = ee.listeners('event')
    l[0] = raiser

    with nt.assert_raises(ItWorkedException) as it_worked:
        ee.emit('event')
