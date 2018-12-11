"""
Enhanced versions of IPython's traitlets.

Adds the following additional behavior:

- Strict construction/validation of config attributes.
- Serialization to/from dictionaries containing only primitives.
- More strict handling of default values than traitlets' built-in behavior.
"""
from contextlib import contextmanager

import traitlets as tr

from . import compat
from .to_primitive import to_primitive, can_convert_to_primitive


@contextmanager
def cross_validation_lock(obj):
    """
    A contextmanager for holding Traited object's cross-validators.

    This should be used in circumstances where you want to call _validate, but
    don't want to fire cross-validators.
    """
    # TODO: Replace this with usage of public API when
    # https://github.com/ipython/traitlets/pull/166 lands upstream.
    orig = getattr(obj, '_cross_validation_lock', False)
    try:
        obj._cross_validation_lock = True
        yield
    finally:
        obj._cross_validation_lock = orig


class SerializableTrait(tr.TraitType):

    # Override IPython's default values with Undefined so that default values
    # must be passed explicitly to trait instances.
    default_value = tr.Undefined

    def example(self, value):
        return self.tag(example=value)

    def instance_init(self, obj):
        super(SerializableTrait, self).instance_init(obj)
        # If we were tagged with an example, make sure it's actually a valid
        # example.
        example = self._static_example_value()
        if example is not tr.Undefined:
            with cross_validation_lock(obj):
                self._validate(obj, example)

    def _static_example_value(self):
        return self.metadata.get('example', self.default_value)

    example_value = property(_static_example_value)


class Integer(SerializableTrait, tr.Integer):
    pass


class Float(SerializableTrait, tr.Float):
    pass


class Unicode(SerializableTrait, tr.Unicode):
    pass


class LengthBoundedUnicode(Unicode):

    def __init__(self, minlen, maxlen, *args, **kwargs):
        self.minlen = minlen
        self.maxlen = maxlen
        super(LengthBoundedUnicode, self).__init__(*args, **kwargs)

    def validate(self, obj, value):
        super_retval = super(LengthBoundedUnicode, self).validate(obj, value)
        length = len(value)
        if length < self.minlen:
            raise tr.TraitError("len(%r) < minlen=%d" % (value, self.minlen))
        elif length > self.maxlen:
            raise tr.TraitError("len(%r) > maxlen=%d" % (value, self.maxlen))
        return super_retval


class Bool(SerializableTrait, tr.Bool):
    pass


# Different traitlets container types use different values for `default_value`.
# Figure out what to use by inspecting the signatures of __init__.
def _get_default_value_sentinel(t):
    # traitlets Tuple does a kwargs.pop rather than specifying the value in its
    # signature.
    if t is tr.Tuple:
        return tr.Undefined
    argspec = compat.argspec(t.__init__)
    for name, value in zip(reversed(argspec.args), reversed(argspec.defaults)):
        if name == 'default_value':
            return value

    raise TypeError(  # pragma: nocover
        "Can't find default value sentinel for type %s" % t
    )


_NOTPASSED = object()
_TRAITLETS_CONTAINER_TYPES = frozenset([tr.List, tr.Set, tr.Dict, tr.Tuple])
_DEFAULT_VALUE_SENTINELS = {
    t: _get_default_value_sentinel(t) for t in _TRAITLETS_CONTAINER_TYPES
}


class _ContainerMixin(object):

    def __init__(self, default_value=_NOTPASSED, **kwargs):
        # traitlets' Container base class converts default_value into args and
        # kwargs to pass to a factory type and sets those values to (), {} when
        # default is None or Undefined.  They do this so that not every List
        # trait shares the same list object as a default value, but each
        # subclass mucks with the default value in slightly different ways, and
        # all of them interpret 'default_value not passed' as 'construct an
        # empty instance', which we don't think is a sane choice of default.
        #
        # Rather than trying to intercept all the different ways that traitlets
        # overrides default values, we just mark whether we've seen an explicit
        # default value in our constructor, and our make_dynamic_default
        # function yields Undefined if this wasn't specified.
        self._have_explicit_default_value = (default_value is not _NOTPASSED)
        if not self._have_explicit_default_value:
            # Different traitlets use different values in their __init__
            # signatures to signify 'not passed'.  Find the correct value to
            # forward by inspecting our method resolution order.
            for type_ in type(self).mro():
                if type_ in _TRAITLETS_CONTAINER_TYPES:
                    default_value = _DEFAULT_VALUE_SENTINELS[type_]
                    break
            else:  # pragma: nocover
                raise tr.TraitError(
                    "_ContainerMixin applied to unknown type %s" % type(self)
                )

        super(_ContainerMixin, self).__init__(
            default_value=default_value,
            **kwargs
        )

    def validate(self, obj, value):
        # Ensure that the value is coercible to a primitive.
        to_primitive(value)
        return super(_ContainerMixin, self).validate(obj, value)

    def make_dynamic_default(self):
        if not self._have_explicit_default_value:
            return None
        return super(_ContainerMixin, self).make_dynamic_default()


class Set(SerializableTrait, _ContainerMixin, tr.Set):
    pass


class List(SerializableTrait, _ContainerMixin, tr.List):
    pass


class Dict(SerializableTrait, _ContainerMixin, tr.Dict):
    pass


class Tuple(SerializableTrait, _ContainerMixin, tr.Tuple):
    pass


class Enum(SerializableTrait, tr.Enum):

    def __init__(self, *args, **kwargs):
        super(Enum, self).__init__(*args, **kwargs)
        for value in self.values:
            if not can_convert_to_primitive(type(value)):
                raise TypeError(
                    "Can't convert Enum value %s to a primitive." % value
                )


class Instance(SerializableTrait, tr.Instance):

    def __init__(self, *args, **kwargs):
        super(Instance, self).__init__(*args, **kwargs)
        self._resolve_classes()
        if not can_convert_to_primitive(self.klass):
            raise TypeError(
                "Can't convert instances of %s to primitives." % (
                    self.klass.__name__,
                )
            )

    def validate(self, obj, value):
        from .serializable import Serializable
        if issubclass(self.klass, Serializable) and isinstance(value, dict):
            value = self.klass.from_dict(value)
        return super(Instance, self).validate(obj, value)

    @property
    def example_value(self):
        """
        If we're an instance of a Serializable, fall back to its
        `example_instance()` method.
        """
        from .serializable import Serializable
        inst = self._static_example_value()
        if inst is tr.Undefined and issubclass(self.klass, Serializable):
            return self.klass.example_instance()
        return inst

    # Override the base class.
    make_dynamic_default = None
