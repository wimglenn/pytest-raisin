def default_compare(exc_actual, exc_expected):
    __tracebackhide__ = True
    actual_args = getattr(exc_actual, "args", None)
    expected_args = getattr(exc_expected, "args", None)
    if actual_args == expected_args:
        return
    msg = "{} args do not match!\n    Actual:   {}\n    Expected: {}"
    msg = msg.format(type(exc_expected).__name__, actual_args, expected_args)
    assert 0, msg
