[![pypi](https://img.shields.io/pypi/v/pytest-raisin.svg)](https://pypi.org/project/pytest-raisin/)
![pyversions](https://img.shields.io/pypi/pyversions/pytest-raisin.svg)
[![actions](https://github.com/wimglenn/pytest-raisin/actions/workflows/tests.yml/badge.svg)](https://github.com/wimglenn/pytest-raisin/actions/workflows/tests.yml/)
![image](https://user-images.githubusercontent.com/6615374/50065259-46af2780-017b-11e9-8af3-38f340f11df1.png)

# pytest-raisin

Plugin putting a higher-level interface to
[pytest.raises](https://docs.pytest.org/en/latest/assert.html#assertions-about-expected-exceptions).
It allows to use an exception *instance* as the expected value, which
would be compared with the actual exception (if any) based upon the type
and the `args` attribute.

``` python
# Old-skool:
with pytest.raises(SystemExit) as cm:
    sys.exit(1)
assert cm.value.args == (1,)

# New hotness:
with pytest.raises(SystemExit(1)):
    sys.exit(1)
```

More sophisticated comparisons can be registered for user-defined error
subclasses if necessary (see [Advanced Usage](#advanced-usage)).

## Installation

``` bash
pip install pytest-raisin
```

## Basic Usage

Usage in your tests looks like this

``` python
>>> currant_exchange_rates = {
...     "sultana": 50,
...     "raisins": 100,
... }
>>> with pytest.raises(KeyError("grape")):
...     currant_exchange_rates["grape"]
...
>>> with pytest.raises(KeyError("sultanas")):
...     currant_exchange_rates["prunes"]
...
AssertionError: KeyError args do not match!
    Actual:   ('prunes',)
    Expected: ('sultanas',)

>>> with pytest.raises(KeyError("Carlos Sultana")):
...     currant_exchange_rates["sultana"]
Failed: DID NOT RAISE KeyError('Carlos Sultana')
```

The plugin is enabled by default: `pytest.raises` is monkeypatched with
the new functionality directly. To temporarily execute without the new
stuff, use `pytest -p no:pytest-raisin`.

The various legacy forms of `pytest.raises` will continue to work,
falling back to the original implementation.

## Advanced Usage

In most use-cases, the default behaviour of considering exceptions to be
equivalent if the [args]{.title-ref} attributes have matching tuples
should be satisfactory. However, some 3rd-party exception classes have
additional logic inside them (e.g. Django\'s `ValidationError`) and you
might want to provide a more custom assertion here.

Plugin users may register their own errors/callables via
pytest-raisin\'s decorator factory:

``` python
@pytest.register_exception_compare(MyError)
def my_error_compare(exc_actual, exc_expected):
    ...
```

Your comparison function will be called with the arguments `exc_actual`
and `exc_expected`, which will *both* be directly instances of `MyError`
(the test will have failed earlier if the type was not an exact match).
This function should inspect the instances and raise an `AssertionError`
with useful context message should they be considered not to match. It
should do nothing (i.e. return `None`) if the exceptions should be
considered equivalent.

**Note:** An instance of a subclass is *not* permitted when using an
exception instance as the argument to `pytest.raises`. If you want to
allow subclassing, use the original syntax of passing the type.
