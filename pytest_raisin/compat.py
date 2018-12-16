import sys

if sys.version_info < (3,):
    from pytest_raisin.comparison_py2 import default_compare
else:
    from pytest_raisin.comparison_py3 import default_compare
