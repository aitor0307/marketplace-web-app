import logging
import traceback


class _AppLogger:
    """Thin wrapper around stdlib logging that adds ``catch_exception``.

    Delegates every other attribute (``error``, ``info``, ``exception``, ...)
    straight to a normal ``logging.Logger`` so this is a drop-in stand-in
    wherever plain ``logging.getLogger(...)`` would be used.
    """

    def __init__(self, name):
        self._logger = logging.getLogger(name)

    def __getattr__(self, item):
        return getattr(self._logger, item)

    def catch_exception(self, exc):
        self._logger.error("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))


logger = _AppLogger("marketplace")
