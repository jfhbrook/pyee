# -*- coding: utf-8 -*-

from mock import call, Mock
from pyee import BaseEventEmitter, evolve


class UpgradedEventEmitter(BaseEventEmitter):
    pass


def test_evolve():
    call_me = Mock()

    base_ee = BaseEventEmitter()

    @base_ee.on('base_event')
    def base_handler():
        call_me('base_event')

    upgraded_ee = evolve(UpgradedEventEmitter, base_ee)

    assert isinstance(
        upgraded_ee,
        UpgradedEventEmitter
    ), 'Returns an upgraded emitter'

    @upgraded_ee.on('upgraded_event')
    def upgraded_handler():
        call_me('upgraded_event')


    assert upgraded_ee.emit('base_event') is True, 'base event registers as fired on upgraded event emitter'  # noqa
    assert upgraded_ee.emit('upgraded_event') is True, 'upgraded event registers as fired on upgraded event emitter'  # noqa

    call_me.assert_has_calls([
        call('base_event'),
        call('upgraded_event')
    ])

    call_me.reset_mock()

    assert base_ee.emit('base_event') is True, 'base event still registers on base event emitter'  # noqa
    assert base_ee.emit('upgraded_event') is False, 'upgraded event not registered on base event emitter'  # noqa

    call_me.assert_called_once_with('base_event')

    call_me.reset_mock()

    base_ee.remove_listener('base_event', base_handler)

    assert upgraded_ee.emit('base_event') is True, "removing a listener from an underlying event emitter doesn't affect the upgraded event emitter"  # noqa

    call_me.assert_called_once_with('base_event')
