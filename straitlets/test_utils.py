"""
Testing utilities.
"""
from contextlib import contextmanager

import pytest
from six import iteritems

from .serializable import Serializable


def multifixture(g):
    """
    Decorator for turning a generator into a "parameterized" fixture that emits
    the generated values.
    """
    fixture_values = list(g())

    @pytest.fixture(params=fixture_values)
    def _fixture(request):
        return request.param

    return _fixture


def check_attributes(obj, attrs):
    for key, value in iteritems(attrs):
        assert getattr(obj, key) == value


def assert_serializables_equal(left, right):
    assert type(left) == type(right)
    assert set(left.trait_names()) == set(right.trait_names())
    for name in left.trait_names():
        left_attr = getattr(left, name)
        right_attr = getattr(right, name)
        assert type(left_attr) == type(right_attr)
        if isinstance(left_attr, Serializable):
            assert_serializables_equal(left_attr, right_attr)
        else:
            assert left_attr == right_attr


@contextmanager
def removed_key(dict_, key):
    value = dict_.pop(key)
    try:
        yield
    finally:
        dict_[key] = value
