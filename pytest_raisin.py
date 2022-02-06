"""Plugin enabling the use of exception instances with pytest.raises"""
import logging
import sys

import pytest


__version__ = "0.4"


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
    exception_classes = exception_class
    if not isinstance(exception_class, tuple):
        exception_classes = (exception_class,)

    for exception_class in exception_classes:
        if not isinstance(exception_class, type) or not issubclass(exception_class, BaseException):
            msg = "Can not register {!r}, it's not an Exception subclass"
            msg = msg.format(exception_class)
            raise TypeError(msg)

    def decorator(func):
        if not callable(func):
            raise TypeError('You are decorating a non callable: {!r}'.format(func))
        for exception_class in exception_classes:
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
    # There are some strange non-context usages of raises, e.g. passing a callable along
    # with args/kwargs or passing a code string to be exec. I don't want to support those
    # weird use-cases, so just fall-back to original implementation if we received any
    # positional values i.e. a non-empty *args
    return original(expected_exception, *args, **kwargs)


def default_compare(exc_actual, exc_expected):
    __tracebackhide__ = True
    actual_args = getattr(exc_actual, "args", None)
    expected_args = getattr(exc_expected, "args", None)
    if actual_args == expected_args:
        return
    msg = "{} args do not match!\n    Actual:   {}\n    Expected: {}"
    msg = msg.format(type(exc_expected).__name__, actual_args, expected_args)
    err = AssertionError(msg)
    err.__cause__ = None
    # as a side-effect, this also sets __suppress_context__
    # that's a cross-compatible way of disabling chaining i.e. squashing the message
    # "During handling of the above exception, another exception occurred"
    raise err


class RaisesContext(object):
    def __init__(self, expected_exception, message, match_expr=None):
        self.expected_exception = expected_exception
        self.message = message
        self.match_expr = match_expr
        self.excinfo = None

    def __enter__(self):
        if int(pytest.__version__.split(".")[0]) < 7:
            ExceptionInfo = type(pytest.raises(Exception).__enter__())
        else:
            ExceptionInfo = pytest.ExceptionInfo
        self.excinfo = ExceptionInfo.for_later()
        return self.excinfo

    def __exit__(self, exc_type, exc_val, exc_tb):
        __tracebackhide__ = True
        if exc_type is None:
            pytest.fail(self.message)
        if sys.version_info < (3,):
            # very old pytest version e.g. Python 2.x
            self.excinfo.__init__((exc_type, exc_val, exc_tb))
        else:
            self.excinfo.fill_unfilled((exc_type, exc_val, exc_tb))
        # note: subclasses are not allowed here!
        suppress_exception = exc_type is type(self.expected_exception)
        if sys.version_info < (3,) and suppress_exception:
            sys.exc_clear()
        if suppress_exception:
            compare = exception_comparers.get(type(self.expected_exception), default_compare)
            compare(exc_val, self.expected_exception)
        if self.match_expr is not None and suppress_exception:
            self.excinfo.match(self.match_expr)
        return suppress_exception


def pytest_configure(config):
    # this is called once after command line args have been parsed
    pytest.raises = raises
    pytest.register_exception_compare = register_exception_compare


def pytest_unconfigure(config):
    pytest.raises = original
    vars(pytest).pop("register_exception_compare", None)


pytest.register_exception_compare = register_exception_compare
