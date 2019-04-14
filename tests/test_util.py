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
    uplifted_ee.emit('base_event')
    uplifted_ee.emit('shared_event')
    uplifted_ee.emit('uplifted_event')

    call_me.assert_has_calls([
        call('base event on base emitter'),
        call('shared event on uplifted emitter'),
        call('shared event on base emitter'),
        call('uplifted event on uplifted emitter')
    ])

    call_me.reset_mock()

    # Events on underlying proxy correctly
    base_ee.emit('base_event')
    base_ee.emit('shared_event')
    base_ee.emit('uplifted_event')

    call_me.assert_has_calls([
        call('base event on base emitter'),
        call('shared event on base emitter'),
        call('shared event on uplifted emitter'),
        call('uplifted event on uplifted emitter')
    ])

    call_me.reset_mock()

    # Exception handling alwyas prefers uplifted
    base_exc = Exception('error from base')
    uplifted_exc = Exception('error from uplifted')

    uplifted_ee.on('error', call_me)

    uplifted_ee.emit('error', uplifted_exc)
    base_ee.emit('error', base_exc)

    call_me.assert_has_calls([
        call(uplifted_exc),
        call(base_exc)
    ])
