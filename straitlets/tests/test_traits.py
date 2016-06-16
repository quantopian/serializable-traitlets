import pytest

import traitlets as tr

from ..serializable import Serializable
from ..traits import Enum, LengthBoundedUnicode


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


def test_length_bounded_unicode():

    class F(Serializable):
        u = LengthBoundedUnicode(minlen=5, maxlen=10)

    for i in range(5, 11):
        F(u=u'a' * i)

    with pytest.raises(tr.TraitError):
        F(u=u'a' * 4)

    with pytest.raises(tr.TraitError):
        F(u=u'a' * 11)
