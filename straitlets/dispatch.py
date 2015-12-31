"""
Python <= 3.4 compat for singledispatch.
"""
from sys import version_info
if (version_info.major, version_info.minor) < (3, 4):  # pragma: no cover
    from singledispatch import singledispatch
else:  # pragma: no cover
    from functools import singledispatch

__all__ = ['singledispatch']
