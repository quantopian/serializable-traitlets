import pytest

from straitlets.utils import merge


def test_merge():
    with pytest.raises(ValueError):
        merge()

    d1 = {'a': 'b'}
    assert merge(d1) == d1

    d2 = {'c': 'd'}
    assert merge(d1, d2) == {'a': 'b', 'c': 'd'}

    d3 = {'a': 'z', 'e': 'f'}
    assert merge(d1, d2, d3) == {'a': 'z', 'c': 'd', 'e': 'f'}
