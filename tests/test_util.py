# -*- coding: utf-8 -*-

from mock import call, Mock
from pyee import BaseEventEmitter
from pyee.util import uplift


class UpliftedEventEmitter(BaseEventEmitter):
    pass


def test_uplift():
    call_me = Mock()

    base_ee = BaseEventEmitter()

    @base_ee.on('base_event')
    def base_handler():
        call_me('base event on base emitter')

    @base_ee.on('shared_event')
    def shared_base_handler():
        call_me('shared event on base emitter')

    uplifted_ee = uplift(UpliftedEventEmitter, base_ee)

    assert isinstance(
        uplifted_ee,
        UpliftedEventEmitter
    ), 'Returns an uplifted emitter'

    @uplifted_ee.on('uplifted_event')
    def uplifted_handler():
        call_me('uplifted event on uplifted emitter')

    @uplifted_ee.on('shared_event')
    def shared_uplifted_handler():
        call_me('shared event on uplifted emitter')

    # Events on uplifted proxy correctly
    assert uplifted_ee.emit('base_event')
    assert uplifted_ee.emit('shared_event')
    assert uplifted_ee.emit('uplifted_event')

    call_me.assert_has_calls([
        call('base event on base emitter'),
        call('shared event on uplifted emitter'),
        call('shared event on base emitter'),
        call('uplifted event on uplifted emitter')
    ])

    call_me.reset_mock()

    # Events on underlying proxy correctly
    assert base_ee.emit('base_event')
    assert base_ee.emit('shared_event')
    assert base_ee.emit('uplifted_event')

    call_me.assert_has_calls([
        call('base event on base emitter'),
        call('shared event on base emitter'),
        call('shared event on uplifted emitter'),
        call('uplifted event on uplifted emitter')
    ])

    call_me.reset_mock()

    # Exception handling alwyas prefers uplifted

    base_error = Exception('base error')
    uplifted_error = Exception('uplifted error')

    # Hold my beer
    error_handler = Mock()
    original_error_handler = uplifted_ee._emit_handle_potential_error
    uplifted_ee._emit_handle_potential_error = error_handler

    base_ee.emit('error', base_error)
    uplifted_ee.emit('error', uplifted_error)

    error_handler.has_calls([
        call('error', base_error),
        call('error', uplifted_error)
    ])

    uplifted_ee._emit_handle_potential_error = original_error_handler

    # Quick check for unwrap
    uplifted_ee.unwrap()

    assert not uplifted_ee.emit('base_event')
    assert uplifted_ee.emit('shared_event')
    assert uplifted_ee.emit('uplifted_event')

    assert base_ee.emit('base_event')
    assert base_ee.emit('shared_event')
    assert not base_ee.emit('uplifted_event')

    call_me.assert_has_calls([
        # No listener for base event on uplifted
        call('shared event on uplifted emitter'),
        call('uplifted event on uplifted emitter'),
        call('base event on base emitter'),
        call('shared event on base emitter')
        # No listener for uplifted event on uplifted
    ])
