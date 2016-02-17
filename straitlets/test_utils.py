"""
Testing utilities.
"""
from contextlib import contextmanager

import pytest
from six import iteritems, string_types
from six.moves.urllib.parse import parse_qs

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


def assert_serializables_equal(left, right, skip=()):
    assert type(left) == type(right)
    assert set(left.trait_names()) == set(right.trait_names())
    for name in left.trait_names():
        if name in skip:
            continue
        left_attr = getattr(left, name)
        right_attr = getattr(right, name)
        assert type(left_attr) == type(right_attr)
        if isinstance(left_attr, Serializable):
            assert_serializables_equal(left_attr, right_attr)
        else:
            assert left_attr == right_attr


def assert_urls_equal(left, right):
    assert isinstance(left, string_types)
    assert isinstance(right, string_types)

    left_parts = left.split('?', 1)
    right_parts = right.split('?', 1)

    left_url = left_parts[0]
    right_url = right_parts[0]
    assert left_url == right_url

    left_params = left_parts[1:]
    right_params = right_parts[1:]
    assert len(left_params) == len(right_params)
    if left_params:
        assert parse_qs(left_params[0]) == parse_qs(right_params[0])


@contextmanager
def removed_keys(dict_, keys):
    popped = {}
    for key in keys:
        popped[key] = dict_.pop(key)
    try:
        yield
    finally:
        dict_.update(popped)
