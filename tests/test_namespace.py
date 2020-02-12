# -*- coding: utf-8 -*-
from collections import OrderedDict

from mock import Mock
from pytest import raises

from pyee.namespace import NamespaceEventEmitter


class PyeeTestException(Exception):
    pass


def test_emit_simple():
    ee = NamespaceEventEmitter()
    call_me = Mock()

    # Register listener
    ee.on('event', call_me)

    ee.emit('event', 1, 2, 3, test="wow")

    call_me.assert_called_with(1, 2, 3, test="wow")

    ee.emit(('event',), 4, 5, 6, test="much")

    call_me.assert_called_with(4, 5, 6, test="much")


def test_emit_namespace_single_level():
    ee = NamespaceEventEmitter()
    call_me = Mock()

    # Register listener
    ee.on(('event', ), call_me)

    ee.emit('event', 1, 2, 3, test="wow")

    call_me.assert_called_with(1, 2, 3, test="wow")

    ee.emit(('event',), 4, 5, 6, test="much")

    call_me.assert_called_with(4, 5, 6, test="much")


def test_emit_namespace_multi_level():
    ee = NamespaceEventEmitter()
    call_me = Mock()

    # Register listener
    ee.on(('event', 'level', 'type'), call_me)

    ee.emit(('event', 'level', 'type'), 1, 2, 3, test="wow")

    call_me.assert_called_with(1, 2, 3, test="wow")


def test_listener_namespace_multi_level():
    ee = NamespaceEventEmitter()
    call_me1 = Mock()
    call_me2 = Mock()
    call_me3 = Mock()

    # Register listener
    ee.on(('event', 'level'), call_me2)
    ee.on(('event', 'level', 'type'), call_me3)
    ee.on(('event',), call_me1)

    ee.emit(('event', 'level', 'type'), 1, 2, 3, test="wow")

    call_me1.assert_called_with(1, 2, 3, test="wow")
    call_me2.assert_called_with(1, 2, 3, test="wow")
    call_me3.assert_called_with(1, 2, 3, test="wow")
