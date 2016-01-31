import pytest
from ..to_primitive import to_primitive


def test_base_case():
    class SomeRandomClass(object):
        pass

    with pytest.raises(TypeError) as e:
        to_primitive(SomeRandomClass())

    assert str(e.value) == (
        "Don't know how to convert instances of SomeRandomClass to primitives."
    )
