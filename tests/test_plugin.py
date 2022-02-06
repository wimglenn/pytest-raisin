import sys


def test_using_exception_class(testdir):
    testdir.makepyfile("""
        import pytest

        def test_name_error_class():
            with pytest.raises(NameError):
                wtf
    """)
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


def test_using_exception_instance(testdir):
    testdir.makepyfile("""
        import pytest

        def test_name_error_instance():
            with pytest.raises(IndexError("list index out of range")):
                [][0]
    """)
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


def test_using_exception_instance_wrong_args(testdir):
    testdir.makepyfile("""
        import pytest

        def test_index_error_instance():
            with pytest.raises(IndexError("Hello, I am a potato")):
                [][0]
    """)
    result = testdir.runpytest()
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "test_using_exception_instance_wrong_args.py F *",
        "E * AssertionError: IndexError args do not match!",
        "E *   Actual:   ('list index out of range',)",
        "E *   Expected: ('Hello, I am a potato',)",
    ])


def test_using_exception_instance_wrong_type(testdir):
    testdir.makepyfile("""
        import pytest

        def test_index_error_instance():
            with pytest.raises(LookupError("list index out of range")):
                [][0]
    """)
    result = testdir.runpytest()
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "test_using_exception_instance_wrong_type.py F *",
        "test_using_exception_instance_wrong_type.py:5: IndexError",
    ])


def test_failure_to_raise_uses_full_repr(testdir):
    testdir.makepyfile("""
        import pytest

        def test_no_raise():
            with pytest.raises(SystemExit(2, 'bye')):
                pass
    """)
    result = testdir.runpytest()
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "test_failure_to_raise_uses_full_repr.py F *",
        "E * Failed: DID NOT RAISE SystemExit(2, 'bye')",
    ])


def test_using_exception_instance_and_regex_matches(testdir):
    testdir.makepyfile("""
        import pytest

        def test_name_error_instance():
            with pytest.raises(Exception("somebody set up us the bomb"), match="bomb"):
                raise Exception("somebody set up us the bomb")
    """)
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


def test_using_exception_instance_and_regex_doesnt_match(testdir):
    testdir.makepyfile("""
        import pytest

        def test_name_error_instance():
            with pytest.raises(Exception("somebody set up us the bomb"), match="2101"):
                raise Exception("somebody set up us the bomb")
    """)
    result = testdir.runpytest()
    result.assert_outcomes(failed=1)
    if sys.version_info.major == 2:
        txt = "E * AssertionError: Pattern '2101' not found in 'somebody set up us the bomb'"
    else:
        txt = "E * AssertionError: Regex pattern '2101' does not match 'somebody set up us the bomb'."
    result.stdout.fnmatch_lines([txt])
