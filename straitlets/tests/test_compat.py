# encoding: utf-8
import sys

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


@pytest.mark.skipif(
    sys.version_info.major > 2,
    reason='we can import straitlets.py3 in Python 3',
)
def test_py3_import_error():  # pragma: no cover
    with pytest.raises(ImportError) as e:
        import straitlets.py3  # noqa

    assert str(e.value) == 'straitlets.py3 is only available in Python 3'
