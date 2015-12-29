"""
Defines a Serializable subclass for extended traitlets.
"""
import json
from textwrap import dedent
import yaml

from traitlets import MetaHasTraits, TraitType, HasTraits
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


_DID_YOU_MEAN_INSTANCE_TEMPLATE = dedent(
    """
    {type}.__init__() got unexpected keyword argument {name!r}.
    {type} (or a parent) has a class attribute with the same name.
    Did you mean to write `{name} = Instance({instance_type})`?
    """
)


class Serializable(with_metaclass(SerializableMeta, HasTraits)):
    """
    Base class for HasTraits instances that can be serialized into Python
    primitives.

    The traitlets set on Serializables must be instances of
    straitlets.traits.SerializableTrait.
    """
    def __init__(self, *args, **metadata):
        unexpected = viewkeys(metadata) - self.trait_names()
        if unexpected:
            raise TypeError(self._unexpected_kwarg_msg(unexpected))
        super(Serializable, self).__init__(*args, **metadata)

    @classmethod
    def _unexpected_kwarg_msg(cls, unexpected):
        # Provide a more useful error is the user did:
        #
        #     class SomeSerializable(Serializable):
        #         sub_serial = SomeOtherSerializable()
        #
        # When what they actually meant was:
        #     class SomeSerializable(Serializable):
        #         sub_serial = Instance(SomeOtherSerializable)
        for name in unexpected:
            not_there = object()
            maybe_attr = getattr(cls, name, not_there)
            if maybe_attr is not not_there:
                return _DID_YOU_MEAN_INSTANCE_TEMPLATE.format(
                    type=cls.__name__,
                    name=name,
                    instance_type=type(maybe_attr).__name__,
                )
        return (
            "{type}.__init__() got unexpected"
            " keyword arguments {unexpected}.".format(
                type=cls.__name__,
                unexpected=tuple(unexpected),
            )
        )

    def to_dict(self):
        out_dict = {}
        for key in self.trait_names():
            out_dict[key] = to_primitive(getattr(self, key))
        return out_dict

    @classmethod
    def from_dict(cls, dict_):
        return cls(**dict_)

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, s):
        return cls.from_dict(json.loads(s))

    def to_yaml(self):
        return yaml.safe_dump(self.to_dict())

    @classmethod
    def from_yaml(cls, stream):
        return cls.from_dict(yaml.safe_load(stream))

    @classmethod
    def from_yaml_file(cls, path):
        with open(path, 'r') as f:
            return cls.from_yaml(f)


@to_primitive.register(Serializable)
def _serializable_to_primitive(s):
    return s.to_dict()
