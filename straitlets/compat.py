from six import PY3

if PY3:
    long = int
    unicode = str
else:
    long = long
    unicode = unicode
