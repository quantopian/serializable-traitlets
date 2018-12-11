from six import iterkeys, itervalues
from six.moves import zip, map

from straitlets.compat import long, unicode
from straitlets.dispatch import singledispatch


@singledispatch
def to_primitive(obj):
    raise TypeError(
        "Don't know how to convert instances of %s to primitives." % (
            type(obj).__name__
        )
    )


_base_handler = to_primitive.dispatch(object)


def can_convert_to_primitive(type_):
    """
    Check whether or not we have a to_primitive handler type_.
    """
    return to_primitive.dispatch(type_) is not _base_handler


@to_primitive.register(int)
@to_primitive.register(long)  # Redundant in PY3, but that's fine.
@to_primitive.register(float)
@to_primitive.register(unicode)
@to_primitive.register(bytes)
@to_primitive.register(type(None))
def _atom_to_primitive(a):
    return a


@to_primitive.register(set)
@to_primitive.register(list)
@to_primitive.register(tuple)
@to_primitive.register(frozenset)
def _sequence_to_primitive(s):
    return list(map(to_primitive, s))


@to_primitive.register(dict)
def _dict_to_primitive(d):
    return dict(
        zip(
            map(to_primitive, iterkeys(d)),
            map(to_primitive, itervalues(d)),
        )
    )
