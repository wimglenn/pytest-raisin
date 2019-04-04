def test_spurious_chaining_is_suppressed(testdir):
    testdir.makepyfile("""
        import pytest

        def test_the_thing():
            with pytest.raises(Exception("boom")):
                raise Exception("bang")
    """)
    result = testdir.runpytest()
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "E * AssertionError: Exception args do not match!",
        "E *   Actual:   ('bang',)",
        "E *   Expected: ('boom',)",
    ])
    text = result.stdout.str()
    assert "During handling of the above exception, another exception occurred" not in text
