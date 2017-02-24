import sys

import pytest
import traitlets as tr

from ..serializable import Serializable
from ..test_utils import assert_serializables_equal
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


@pytest.mark.skipif(
    sys.version_info.major < 3,
    reason='Path requires Python 3',
)
def test_path(roundtrip_func):  # pragma: no cover
    # defer imports because these only work in Python 3
    import pathlib
    from ..py3 import Path

    class S(Serializable):
        p = Path()

    s = S(p='/etc')

    # ensure that the object stored at ``p`` is a ``pathlib.Path``
    assert isinstance(s.p, pathlib.Path)

    assert_serializables_equal(s, roundtrip_func(s))
