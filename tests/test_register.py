pytest_plugins = ["pytester"]


def test_user_registered_error_hook_pass(testdir):
    testdir.makepyfile("""
        import pytest

        class MyError(Exception):
            def __init__(self, code):
                self.code = code

        @pytest.register_exception_compare(MyError)
        def my_error_compare(exc_actual, exc_expected):
            assert exc_actual.code == exc_expected.code, 'user wtf message'

        def test_user_registered_pass():
            with pytest.raises(MyError(2)):
                raise MyError(2)
    """)
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


def test_user_registered_error_hook_fail(testdir):
    testdir.makepyfile("""
        import pytest

        class MyError(Exception):
            def __init__(self, code):
                self.code = code

        @pytest.register_exception_compare(MyError)
        def my_error_compare(exc_actual, exc_expected):
            assert exc_actual.code == exc_expected.code, 'user wtf message'

        def test_user_registered_pass():
            with pytest.raises(MyError(2)):
                raise MyError("two")
    """)
    result = testdir.runpytest()
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "E * AssertionError: user wtf message"
    ])
