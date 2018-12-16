"""Plugin enabling the use of exception instances with pytest.raises"""
import logging
import sys

import pytest

from pytest_raisin.compat import default_compare


__version__ = "0.1"


log = logging.getLogger(__name__)


original = pytest.raises


# Mapping of exception subclasses (keys) to callables (values).
exception_comparers = {}


def register_exception_compare(exception_class):
    """Plugin users may register their own errors/callables here by
    placing pytest-raisin's decorator factory above a function:

        @pytest.register_exception_compare(MyError)
        def my_error_compare(exc_actual, exc_expected):
            ...

    The arguments exc_actual and exc_expected should be instances
    of MyError. The function should raise an AssertionError with
    useful context message should they fail to match. It should
    return None if the exceptions should be considered equivalent.
    """

    if not isinstance(exception_class, type) or not issubclass(exception_class, BaseException):
        msg = "Can not register {!r}, it's not an Exception subclass"
        msg = msg.format(exception_class)
        raise TypeError(msg)

    def decorator(func):
        if not callable(func):
            raise TypeError('You are decorating a non callable: {!r}'.format(func))
        if exception_class in exception_comparers:
            log.warning("%r was registered multiple times", exception_class)
        exception_comparers[exception_class] = func
        log.debug("Registered %r to handle %r comparisons", func, exception_class)
        return func

    return decorator


def raises(expected_exception, *args, **kwargs):
    """Monkeypatched in by pytest-raisin plugin"""
    if isinstance(expected_exception, BaseException) and not args and "message" not in kwargs:
        message = "DID NOT RAISE {!r}".format(expected_exception)
        return RaisesContext(expected_exception, message, kwargs.get("match"))
    return original(expected_exception, *args, **kwargs)


class RaisesContext(type(pytest.raises(Exception))):

    def __exit__(self, *tp):
        __tracebackhide__ = True
        if tp[0] is None:
            pytest.fail(self.message)
        self.excinfo.__init__(tp)
        # note: subclasses are not allowed here!
        suppress_exception = self.excinfo.type is type(self.expected_exception)
        if sys.version_info < (3,) and suppress_exception:
            sys.exc_clear()
        if suppress_exception:
            compare = exception_comparers.get(type(self.expected_exception), default_compare)
            compare(self.excinfo.value, self.expected_exception)
        if self.match_expr is not None and suppress_exception:
            self.excinfo.match(self.match_expr)
        return suppress_exception


def pytest_configure(config):
    # this is called once after command line args have been parsed
    pytest.raises = raises
    pytest.register_exception_compare = register_exception_compare


def pytest_unconfigure(config):
    pytest.raises = original
    vars(pytest).pop("register_exception_comparer", None)
