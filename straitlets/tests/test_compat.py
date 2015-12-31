# encoding: utf-8
import pytest

from ..compat import ensure_bytes, ensure_unicode


def test_ensure_bytes():

    b = b"asdfas"
    u = u'unicodé'

    assert ensure_bytes(b) is b
    assert ensure_bytes(u) == b"unicod\xc3\xa9"

    with pytest.raises(TypeError):
        ensure_bytes(1)


def test_ensure_unicode():

    b = b"asdfas"
    u = u'unicodé'

    assert ensure_unicode(b) == u"asdfas"
    assert ensure_unicode(u) is u

    with pytest.raises(TypeError):
        ensure_unicode(1)
