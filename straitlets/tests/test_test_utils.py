"""
Tests for the test utils.
"""
import pytest

from straitlets import Serializable, Integer
from straitlets.test_utils import assert_serializables_equal


def test_assert_serializables_equal():

    class Foo(Serializable):
        x = Integer()
        y = Integer()

    class Bar(Serializable):
        x = Integer()
        y = Integer()

    assert_serializables_equal(Foo(x=1, y=1), Foo(x=1, y=1))

    with pytest.raises(AssertionError):
        assert_serializables_equal(Foo(x=1, y=1), Bar(x=1, y=1))

    with pytest.raises(AssertionError):
        assert_serializables_equal(Foo(x=1, y=1), Foo(x=1, y=2))
    with pytest.raises(AssertionError):
        assert_serializables_equal(
            Foo(x=1, y=1),
            Foo(x=1, y=2),
            skip=('x',),
        )

    assert_serializables_equal(Foo(x=1), Foo(x=1), skip=('y',))
    assert_serializables_equal(Foo(y=1), Foo(y=1), skip=('x',))
