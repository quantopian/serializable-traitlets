"""
Defines a Serializable subclass for extended traitlets.
"""
import json
import base64
from textwrap import dedent
import yaml

from traitlets import (
    HasTraits,
    MetaHasTraits,
    TraitType,
    Undefined,
)
from six import with_metaclass, iteritems, viewkeys

from .compat import ensure_bytes, ensure_unicode
from .traits import SerializableTrait
from .to_primitive import to_primitive


class SerializableMeta(MetaHasTraits):

    def __new__(mcls, name, bases, classdict):
        # Check that all TraitType instances are all.
        for maybe_trait_name, maybe_trait_instance in iteritems(classdict):
            if isinstance(maybe_trait_instance, TraitType):
                if not isinstance(maybe_trait_instance, SerializableTrait):
                    raise TypeError(
                        "Got non-serializable trait {name}={type}".format(
                            name=maybe_trait_name,
                            type=type(maybe_trait_instance).__name__,
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

    def __init__(self, **metadata):
        unexpected = viewkeys(metadata) - self.trait_names()
        if unexpected:
            raise TypeError(self._unexpected_kwarg_msg(unexpected))
        super(Serializable, self).__init__(**metadata)

    def validate_all_attributes(self):
        """
        Force validation of all traits.

        Useful for circumstances where an attribute won't be accessed until
        well after construction, but we want to fail eagerly if that attribute
        is passed incorrectly.

        Consider using ``StrictSerializable`` for classes where you always want
        this called on construction.

        See Also
        --------
        StrictSerializable
        """
        for name in self.trait_names():
            getattr(self, name)

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

    @classmethod
    def example_instance(cls):
        """
        Generate an example instance of a Serializable subclass.

        If traits have been tagged with an `example` value, then we use that
        value.  Otherwise we fall back the default_value for the instance.
        """
        kwargs = {}
        for name, trait in iteritems(cls.class_traits()):
            value = trait.example_value
            if value is Undefined:
                continue
            kwargs[name] = value

        return cls(**kwargs)

    @classmethod
    def example_yaml(cls):
        """
        Generate an example yaml string for a Serializable subclass.

        If traits have been tagged with an `example` value, then we use that
        value.  Otherwise we fall back the default_value for the instance.
        """
        return cls.example_instance().to_yaml()

    @classmethod
    def write_example_yaml(cls, dest):
        """
        Write a file containing an example yaml string for a Serializable
        subclass.
        """
        # Make sure we can make an instance before we open a file.
        inst = cls.example_instance()
        with open(dest, 'w') as f:
            inst.to_yaml(stream=f)

    def to_dict(self):
        out_dict = {}
        for key in self.trait_names():
            # Don't serialize the `strict` traitlet.
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

    def to_yaml(self, stream=None):
        return yaml.safe_dump(
            self.to_dict(),
            stream=stream,
            default_flow_style=False,
        )

    @classmethod
    def from_yaml(cls, stream):
        return cls.from_dict(yaml.safe_load(stream))

    @classmethod
    def from_yaml_file(cls, path):
        with open(path, 'r') as f:
            return cls.from_yaml(f)

    @classmethod
    def from_base64(cls, s):
        """
        Construct from base64-encoded JSON.
        """
        return cls.from_json(ensure_unicode(base64.b64decode(s)))

    def to_base64(self):
        """
        Construct from base64-encoded JSON.
        """
        return base64.b64encode(ensure_bytes(self.to_json(), encoding='utf-8'))

    @classmethod
    def from_environ(cls, environ):
        """
        Deserialize an instance that was written to the environment via
        ``to_environ``.

        Parameters
        ----------
        environ : dict-like
            Dict-like object (e.g. os.environ) from which to read ``self``.
        """
        return cls.from_base64(environ[cls.__name__])

    def to_environ(self, environ):
        """
        Serialize and write self to environ[self._envvar].

        Parameters
        ----------
        environ : dict-like
            Dict-like object (e.g. os.environ) into which to write ``self``.
        """
        environ[ensure_unicode(type(self).__name__)] = (
            ensure_unicode(self.to_base64())
        )


@to_primitive.register(Serializable)
def _serializable_to_primitive(s):
    return s.to_dict()


class StrictSerializable(Serializable):
    """
    Serializable subclass that eagerly evaluates traited attributes after
    construction.

    Useful in circumstances where you want to fail as early as possible when an
    object is malformed.
    """

    def __init__(self, **metadata):
        super(Serializable, self).__init__(**metadata)
        self.validate_all_attributes()
