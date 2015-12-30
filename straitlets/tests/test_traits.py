import pytest

from ..traits import Enum


def test_reject_unknown_enum_value():

    class SomeRandomClass(object):

        def __init__(self, x):
            self.x = x

        def __str__(self):
            return "SomeRandomClass(x=%s)" % self.x

    with pytest.raises(TypeError) as e:
        Enum(values=[SomeRandomClass(3)])

    assert str(e.value) == (
        "Can't convert Enum value SomeRandomClass(x=3) to a primitive."
    )
