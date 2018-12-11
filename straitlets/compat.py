from six import PY3

if PY3:  # pragma: no cover
    from inspect import getfullargspec as argspec  # noqa
    long = int
    unicode = str
else:    # pragma: no cover
    from inspect import getargspec as argspec  # noqa
    long = long
    unicode = unicode


def ensure_bytes(s, encoding='utf-8'):
    if isinstance(s, bytes):
        return s
    elif isinstance(s, unicode):
        return s.encode(encoding=encoding)
    raise TypeError("Expected bytes or unicode, got %s." % type(s))


def ensure_unicode(s, encoding='utf-8'):
    if isinstance(s, unicode):
        return s
    elif isinstance(s, bytes):
        return s.decode(encoding=encoding)
    raise TypeError("Expected bytes or unicode, got %s." % type(s))


__all__ = [
    'argspec',
    'ensure_bytes',
    'ensure_unicode',
    'long',
]
