"""Plugin enabling the use of exception instances with pytest.raises"""
import pytest
import sys

from future.utils import raise_from


__version__ = "0.1"


original = pytest.raises


class RaisesContext(type(pytest.raises(Exception))):

    def __exit__(self, *tp):
        __tracebackhide__ = True
        if tp[0] is None:
            pytest.fail(self.message)
        self.excinfo.__init__(tp)
        type_match = self.excinfo.type is type(self.expected_exception)  # note: subclasses are not allowed
        actual_args = getattr(self.excinfo.value, "args", None)
        expected_args = getattr(self.expected_exception, "args", None)
        args_match = actual_args == expected_args
        suppress_exception = type_match and args_match
        if sys.version_info[0] == 2 and suppress_exception:
            sys.exc_clear()
        if self.match_expr is not None and suppress_exception:
            self.excinfo.match(self.match_expr)
        if type_match and not args_match:
            msg = "{} args do not match!\nActual:   {}\nExpected: {}"
            msg = msg.format(self.excinfo.type.__name__, actual_args, expected_args)
            error = AssertionError(msg)
            raise_from(error, None)
        return suppress_exception


def raisin(expected_exception, *args, **kwargs):
    if isinstance(expected_exception, BaseException) and not args and "message" not in kwargs:
        message = "DID NOT RAISE {!r}".format(expected_exception)
        return RaisesContext(expected_exception, message, kwargs.get("match"))
    return original(expected_exception, *args, **kwargs)


def pytest_configure(config):
    # this is called once after command line args have been parsed
    pytest.raises = raisin


def pytest_unconfigure(config):
    pytest.raises = original
