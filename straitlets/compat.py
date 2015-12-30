from six import PY3

if PY3:  # pragma: no cover
    long = int
    unicode = str
else:    # pragma: no cover
    long = long
    unicode = unicode
