import nose.tools as nt
from pyee import Event_emitter, EventEmitter
from tests import ItWorkedException


def test_patterns():
    """
    Test that patterns are correctly interpreted
    """
    ee = EventEmitter()
    assert ee._matches('#', 'a/b/c')
    assert ee._matches('#/b/c', 'a/b/c')
    assert ee._matches('a/#', 'a/b/c')
    assert not ee._matches('a/#', 'c/a/b/c')
    assert not ee._matches('#/b/c', 'c')
    assert not ee._matches('a/#/d/e', 'a/b/c/d/e')


def test_matching_topic():
    """
    Test that a pattern can be passed as an event
    """

    ee = Event_emitter()

    @ee.on('event/#/ok')
    def event_handler():
        raise ItWorkedException

    with nt.assert_raises(ItWorkedException) as it_worked:
        ee.emit('event/first/ok')

    with nt.assert_raises(ItWorkedException) as it_worked:
        ee.emit('event/second/ok')

    ee.emit('event/first/ok2')


def test_shorter_pattern():
    """
    Tests correct behaviour with shorter patterns
    """
    ee = EventEmitter()

    @ee.on('#')
    def event_handler():
        raise ItWorkedException

    with nt.assert_raises(ItWorkedException) as it_worked:
        ee.emit('a/b/c')

    with nt.assert_raises(ItWorkedException) as it_worked:
        ee.emit('cool')


def test_longer_pattern():
    """
    Tests correct behaviour with longer patterns
    """

    ee = EventEmitter()

    @ee.on('a/b/#')
    def event_handler():
        raise ItWorkedException

    ee.emit('c')

    @ee.on('#/a/b')
    def event_handler():
        raise ItWorkedException('c and #/a/b')

    ee.emit('c')
