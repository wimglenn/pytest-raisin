import logging

import pytest
from pytest_raisin import register_exception_compare


class WhatError:
    pass


class SomeError(Exception):
    pass


def test_cant_register_weird_obj():
    with pytest.raises(TypeError, match="Can not register 123, it's not an Exception subclass"):
        register_exception_compare(123)


def test_cant_register_weird_type():
    with pytest.raises(TypeError, match="Can not register.*WhatError.*it's not an Exception subclass"):
        register_exception_compare(WhatError)


def test_cant_decorate_non_callable():

    dec = register_exception_compare(SomeError)
    with pytest.raises(TypeError, match="You are decorating a non callable: 123"):
        dec(123)


def test_register_twice_is_warned(caplog):
    caplog.set_level(logging.DEBUG)

    @register_exception_compare(SomeError)
    def myfunc(exc_actual, exc_expected):
        pass

    expected_debug_msg = "Registered %r to handle %r comparisons"
    assert caplog.record_tuples == [
        ('pytest_raisin', logging.DEBUG, expected_debug_msg % (myfunc, SomeError))
    ]

    @register_exception_compare(SomeError)
    def myfunc2(exc_actual, exc_expected):
        pass

    expected_warning_msg = "%r was registered multiple times"
    assert caplog.record_tuples == [
        ('pytest_raisin', logging.DEBUG, expected_debug_msg % (myfunc, SomeError)),
        ('pytest_raisin', logging.WARNING, expected_warning_msg % SomeError),
        ('pytest_raisin', logging.DEBUG, expected_debug_msg % (myfunc2, SomeError)),
    ]
