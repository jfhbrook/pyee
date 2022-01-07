# -*- coding: utf-8 -*-

from mock import call, Mock
import pytest

from pyee import EventEmitter
from pyee.uplift import unwrap, uplift


class UpliftedEventEmitter(EventEmitter):
    pass


def test_uplift_emit():
    call_me = Mock()

    base_ee = EventEmitter()

    @base_ee.on("base_event")
    def base_handler():
        call_me("base event on base emitter")

    @base_ee.on("shared_event")
    def shared_base_handler():
        call_me("shared event on base emitter")

    uplifted_ee = uplift(UpliftedEventEmitter, base_ee)

    assert isinstance(uplifted_ee, UpliftedEventEmitter), "Returns an uplifted emitter"

    @uplifted_ee.on("uplifted_event")
    def uplifted_handler():
        call_me("uplifted event on uplifted emitter")

    @uplifted_ee.on("shared_event")
    def shared_uplifted_handler():
        call_me("shared event on uplifted emitter")

    # Events on uplifted proxy correctly
    assert uplifted_ee.emit("base_event")
    assert uplifted_ee.emit("shared_event")
    assert uplifted_ee.emit("uplifted_event")

    call_me.assert_has_calls(
        [
            call("base event on base emitter"),
            call("shared event on uplifted emitter"),
            call("shared event on base emitter"),
            call("uplifted event on uplifted emitter"),
        ]
    )

    call_me.reset_mock()

    # Events on underlying proxy correctly
    assert base_ee.emit("base_event")
    assert base_ee.emit("shared_event")
    assert base_ee.emit("uplifted_event")

    call_me.assert_has_calls(
        [
            call("base event on base emitter"),
            call("shared event on base emitter"),
            call("shared event on uplifted emitter"),
            call("uplifted event on uplifted emitter"),
        ]
    )

    call_me.reset_mock()

    # Quick check for unwrap
    unwrap(uplifted_ee)

    with pytest.raises(AttributeError):
        getattr(uplifted_ee, "unwrap")

    with pytest.raises(AttributeError):
        getattr(base_ee, "unwrap")

    assert not uplifted_ee.emit("base_event")
    assert uplifted_ee.emit("shared_event")
    assert uplifted_ee.emit("uplifted_event")

    assert base_ee.emit("base_event")
    assert base_ee.emit("shared_event")
    assert not base_ee.emit("uplifted_event")

    call_me.assert_has_calls(
        [
            # No listener for base event on uplifted
            call("shared event on uplifted emitter"),
            call("uplifted event on uplifted emitter"),
            call("base event on base emitter"),
            call("shared event on base emitter")
            # No listener for uplifted event on uplifted
        ]
    )


@pytest.mark.parametrize("error_handling", ["new", "underlying", "neither"])
def test_exception_handling(error_handling):
    base_ee = EventEmitter()
    uplifted_ee = uplift(UpliftedEventEmitter, base_ee, error_handling=error_handling)

    # Exception handling always prefers uplifted
    base_error = Exception("base error")
    uplifted_error = Exception("uplifted error")

    # Hold my beer
    base_error_handler = Mock()
    base_ee._emit_handle_potential_error = base_error_handler

    # Hold my other beer
    uplifted_error_handler = Mock()
    uplifted_ee._emit_handle_potential_error = uplifted_error_handler

    base_ee.emit("error", base_error)
    uplifted_ee.emit("error", uplifted_error)

    if error_handling == "new":
        base_error_handler.assert_not_called()
        uplifted_error_handler.assert_has_calls(
            [call("error", base_error), call("error", uplifted_error)]
        )
    elif error_handling == "underlying":
        base_error_handler.assert_has_calls(
            [call("error", base_error), call("error", uplifted_error)]
        )
        uplifted_error_handler.assert_not_called()
    elif error_handling == "neither":
        base_error_handler.assert_called_once_with("error", base_error)
        uplifted_error_handler.assert_called_once_with("error", uplifted_error)
    else:
        raise Exception("unrecognized setting")


@pytest.mark.parametrize(
    "proxy_new_listener", ["both", "neither", "forward", "backward"]
)
def test_proxy_new_listener(proxy_new_listener):
    call_me = Mock()

    base_ee = EventEmitter()

    uplifted_ee = uplift(
        UpliftedEventEmitter, base_ee, proxy_new_listener=proxy_new_listener
    )

    @base_ee.on("new_listener")
    def base_new_listener_handler(event, f):
        assert event in ("event", "new_listener")
        call_me("base new listener handler", f)

    @uplifted_ee.on("new_listener")
    def uplifted_new_listener_handler(event, f):
        assert event in ("event", "new_listener")
        call_me("uplifted new listener handler", f)

    def fresh_base_handler():
        pass

    def fresh_uplifted_handler():
        pass

    base_ee.on("event", fresh_base_handler)
    uplifted_ee.on("event", fresh_uplifted_handler)

    if proxy_new_listener == "both":
        call_me.assert_has_calls(
            [
                call("base new listener handler", fresh_base_handler),
                call("uplifted new listener handler", fresh_base_handler),
                call("uplifted new listener handler", fresh_uplifted_handler),
                call("base new listener handler", fresh_uplifted_handler),
            ]
        )
    elif proxy_new_listener == "neither":
        call_me.assert_has_calls(
            [
                call("base new listener handler", fresh_base_handler),
                call("uplifted new listener handler", fresh_uplifted_handler),
            ]
        )
    elif proxy_new_listener == "forward":
        call_me.assert_has_calls(
            [
                call("base new listener handler", fresh_base_handler),
                call("uplifted new listener handler", fresh_base_handler),
                call("uplifted new listener handler", fresh_uplifted_handler),
            ]
        )
    elif proxy_new_listener == "backward":
        call_me.assert_has_calls(
            [
                call("base new listener handler", fresh_base_handler),
                call("uplifted new listener handler", fresh_uplifted_handler),
                call("base new listener handler", fresh_uplifted_handler),
            ]
        )
    else:
        raise Exception("unrecognized proxy_new_listener")
