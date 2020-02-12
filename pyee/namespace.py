from pyee import BaseEventEmitter

__all__ = ["NamespaceBlacklistException", "NamespaceEventEmitter"]


class NamespaceBlacklistException(Exception):
    pass


class NamespaceEventEmitter(BaseEventEmitter):
    """TODO"""

    NAMESPACE_BLACKLIST = ("new_listener",)

    @classmethod
    def _to_namespace(cls, event):
        if isinstance(event, tuple):
            if len(event) == 0:
                raise ValueError(
                    "Namespace tuples must have at least one entry"
                )

            if event[0] in cls.NAMESPACE_BLACKLIST:
                raise NamespaceBlacklistException(
                    "%s is a blacklisted namespace. It can only be emitted/listened as a simple event"
                )

            return event

        if event in cls.NAMESPACE_BLACKLIST:
            return event

        return (event,)

    def _call_handlers(self, namespace, args, kwargs):
        handled = False

        if isinstance(namespace, tuple):
            for step in range(len(namespace)):
                handled = (
                    super()._call_handlers(namespace[: step + 1], args, kwargs)
                    or handled
                )
        else:
            handled = super()._call_handlers(namespace, args, kwargs)

        return handled

    def _emit_handle_potential_error(self, namespace, error):
        return super()._emit_handle_potential_error(
            "error"
            if isinstance(namespace, tuple) and namespace[0] == "error"
            else namespace,
            error,
        )

    def on(self, event, f=None):
        return super().on(self._to_namespace(event), f)

    def emit(self, event, *args, **kwargs):
        return super().emit(self._to_namespace(event), *args, **kwargs)

    def once(self, event, f=None):
        return super().once(self._to_namespace(event), f)

    def listeners(self, event):
        return super().listeners(self._to_namespace(event))

    def remove_listener(self, event, f):
        return super().remove_listener(self._to_namespace(event), f)

    def remove_all_listeners(self, event=None):
        return super().remove_all_listeners(self._to_namespace(event))


try:
    from pyee._asyncio import AsyncIOEventEmitter  # noqa

    class NamespaceAsyncIOEventEmitter(
        NamespaceEventEmitter, AsyncIOEventEmitter
    ):
        pass

    __all__.append("NamespaceAsyncIOEventEmitter")
except ImportError:
    pass

try:
    from pyee._twisted import TwistedEventEmitter  # noqa

    class NamespaceTwistedEventEmitter(
        NamespaceEventEmitter, TwistedEventEmitter
    ):
        NAMESPACE_BLACKLIST = (
            *NamespaceEventEmitter.NAMESPACE_BLACKLIST,
            "failure",
        )

    __all__.append("NamespaceTwistedEventEmitter")
except ImportError:
    pass

try:
    from pyee._executor import ExecutorEventEmitter  # noqa

    class NamespaceExecutorEventEmitter(
        NamespaceEventEmitter, ExecutorEventEmitter
    ):
        pass

    __all__.append("NamespaceExecutorEventEmitter")
except ImportError:
    pass

try:
    from pyee._trio import TrioEventEmitter  # noqa

    class NamespaceTrioEventEmitter(NamespaceEventEmitter, TrioEventEmitter):
        pass

    __all__.append("NamespaceTrioEventEmitter")
except (ImportError, SyntaxError):
    pass
