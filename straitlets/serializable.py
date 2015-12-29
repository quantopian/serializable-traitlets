"""
Defines a Serializable subclass for extended traitlets.
"""
import json

from traitlets import MetaHasTraits, TraitType
from traitlets.config import Configurable
from six import with_metaclass, iteritems, viewkeys

from .traits import SerializableTrait
from .to_primitive import to_primitive


class SerializableMeta(MetaHasTraits):

    def __new__(mcls, name, bases, classdict):
        # Check that all TraitType instances are all.
        for maybe_trait_name, maybe_trait_instance in iteritems(classdict):
            if isinstance(maybe_trait_instance, TraitType):
                if not isinstance(maybe_trait_instance, SerializableTrait):
                    raise TypeError(
                        "Got non-serializable trait {name}={value}".format(
                            name=maybe_trait_name,
                            value=maybe_trait_instance,
                        )
                    )

        return super(SerializableMeta, mcls).__new__(
            mcls, name, bases, classdict
        )


class Serializable(with_metaclass(SerializableMeta, Configurable)):
    """
    Base class for Configurables that can be serialized into Python primitives.

    There are a few important changes to the semantics of the base Configurable
    class that are necessary to make serializability possible::

        1. Serializable instances are read_only once initialized.
        2. All trait values are evaluated eagerly upon initialization.
        3. Trait values must be instances of SerializableTrait.

    The traitlets set on Serializables must be instances of
    qconfig.traits.SerializableTrait.
    """
    _expected_metadata = set({"help", "config"})

    def __init__(self, *args, **kwargs):
        super(Serializable, self).__init__(*args, **kwargs)

    def init(self):
        unexpected = viewkeys(self.metadata) - self._expected_metadata
        if unexpected:
            raise TypeError(
                "Unexpected metadata in %s: %s" % (
                    type(self.__name__), unexpected
                )
            )

    def to_dict(self):
        return to_primitive(self)

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, dict_):
        return cls(**dict_)

    @classmethod
    def from_json(cls, s):
        return cls.from_dict(json.loads(s))


_no_serialize_keys = frozenset(['parent', 'config'])


@to_primitive.register(Serializable)
def _serializable_to_primitive(s):
    out_dict = {}
    for key in s.trait_names():
        if key in _no_serialize_keys:
            continue
        out_dict[key] = to_primitive(getattr(s, key))
    return out_dict
