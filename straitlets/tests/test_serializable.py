# encoding: utf-8
"""
Tests for serializable.py.
"""
from __future__ import unicode_literals

import re
from textwrap import dedent

import pytest
from traitlets import TraitError, Unicode as base_Unicode

from straitlets.compat import unicode
from straitlets.test_utils import (
    assert_serializables_equal,
    check_attributes,
    multifixture,
)
from ..serializable import (
    MultipleTraitErrors,
    Serializable,
    StrictSerializable,
)
from ..traits import (
    Bool,
    Dict,
    Enum,
    Float,
    Instance,
    Integer,
    List,
    Set,
    Unicode,
    Tuple,
)


not_ascii = 'unicodé'


class Foo(Serializable):

    bool_ = Bool()
    float_ = Float()
    int_ = Integer()
    unicode_ = Unicode()
    enum = Enum(values=(1, 2, not_ascii))

    dict_ = Dict()
    list_ = List()
    set_ = Set()
    tuple_ = Tuple()


@multifixture
def foo_kwargs():
    for seed in (1, 2):
        list_elems = list(range(seed)) + list(map(unicode, range(seed)))
        yield {
            'bool_': bool(seed),
            'float_': float(seed),
            'int_': int(seed),
            'unicode_': unicode(seed),
            'enum': seed,

            'dict_': {
                'a': list_elems,
                not_ascii: list(reversed(list_elems))
            },
            'list_': list_elems,
            'set_': set(list_elems),
            'tuple_': tuple(list_elems),
        }


@multifixture
def skip_names():
    yield ()
    yield ('enum', 'unicode_', 'int_', 'float_', 'bool_')
    yield ('dict_', 'list_', 'set_', 'tuple_')
    yield Foo.class_trait_names()


def test_construct_from_kwargs(foo_kwargs):
    instance = Foo(**foo_kwargs)
    check_attributes(instance, foo_kwargs)


def test_roundtrip(foo_kwargs, roundtrip_func, skip_names):
    foo = Foo(**foo_kwargs)
    roundtripped = roundtrip_func(foo, skip=skip_names)
    assert isinstance(roundtripped, Foo)
    assert foo is not roundtripped
    assert_serializables_equal(roundtripped, foo, skip=skip_names)

    for name in skip_names:
        with pytest.raises(TraitError):
            getattr(roundtripped, name)


class DynamicDefaults(Serializable):

    non_dynamic = Integer()

    d = Dict()
    # This is non-idiomatic usage, but it makes testing simpler.
    DEFAULT_D = {not_ascii: 1}

    def _d_default(self):
        return self.DEFAULT_D

    l = List()  # noqa
    DEFAULT_L = [1, 2, not_ascii, 3]

    def _l_default(self):
        return self.DEFAULT_L


@multifixture
def non_dynamic_val():
    yield 1
    yield 2


@multifixture
def d_val():
    yield {'x': 1}
    yield None


@multifixture
def l_val():
    yield [1, 2, not_ascii]
    yield None


def test_dynamic_defaults(non_dynamic_val, d_val, l_val, roundtrip_func):
    expected = {
        'non_dynamic': non_dynamic_val,
        'd': d_val if d_val is not None else DynamicDefaults.DEFAULT_D,
        'l': l_val if l_val is not None else DynamicDefaults.DEFAULT_L,
    }
    kwargs = {'non_dynamic': non_dynamic_val}
    if d_val is not None:
        kwargs['d'] = d_val
    if l_val is not None:
        kwargs['l'] = l_val

    instance = DynamicDefaults(**kwargs)
    check_attributes(instance, expected)
    check_attributes(roundtrip_func(instance), expected)

    # Do a check without forcing all the attributes via check_attributes.
    check_attributes(roundtrip_func(DynamicDefaults(**kwargs)), expected)


@pytest.fixture
def foo_instance():
    return Foo(
        bool_=True,
        float_=5.0,
        int_=2,
        enum=1,
        unicode_="foo",
        dict_={"foo": "foo"},
        list_=["foo"],
        set_={"foo"},
        tuple_=("foo",),
    )


@pytest.fixture
def different_foo_instance():
    return Foo(
        bool_=False,
        float_=4.0,
        int_=3,
        enum=2,
        unicode_=not_ascii,
        dict_={not_ascii: not_ascii},
        list_=["not_foo", not_ascii, 3],
        set_={"not_foo", not_ascii},
        tuple_=(),
    )


class Nested(Serializable):
    unicode_ = Unicode()
    dict_ = Dict()

    foo1 = Instance(Foo)
    foo2 = Instance(Foo)


@multifixture
def unicode_val():
    yield ""
    yield "ascii"
    yield not_ascii


@multifixture
def dict_val():
    yield {}
    yield {'foo': {'buzz': ['bar']}}


def test_nested(unicode_val,
                dict_val,
                foo_instance,
                different_foo_instance,
                roundtrip_func):

    instance = Nested(
        unicode_=unicode_val,
        dict_=dict_val,
        foo1=foo_instance,
        foo2=different_foo_instance,
    )

    check_attributes(
        instance,
        {
            "unicode_": unicode_val,
            "dict_": dict_val,
        }
    )
    assert_serializables_equal(instance.foo1, foo_instance)
    assert_serializables_equal(instance.foo2, different_foo_instance)

    roundtripped = roundtrip_func(instance)
    assert_serializables_equal(instance, roundtripped)


def test_double_nested(roundtrip_func):

    class Bottom(Serializable):
        x = List()
        y = Unicode()

    class Middle(Serializable):
        x = Integer()
        bottom = Instance(Bottom)

    class Top(Serializable):
        x = Unicode()
        y = Tuple()
        middle = Instance(Middle)

    top = Top(
        x="asdf",
        y=(1, 2),
        middle=Middle(
            x=3,
            bottom=Bottom(
                x=[1, 2],
                y="foo",
            )
        )
    )

    assert_serializables_equal(roundtrip_func(top), top)


def test_inheritance(roundtrip_func, foo_instance):

    class Parent(Serializable):
        a = Integer()

        def _a_default(self):
            return 3

        b = Unicode()

    check_attributes(Parent(b="b"), {"a": 3, "b": "b"})

    class Child(Parent):
        x = Instance(Foo)
        y = Dict()

        def _a_default(self):
            return 4

    child = Child(b="b", x=foo_instance, y={})
    check_attributes(child, {'a': 4, 'b': 'b', 'y': {}})
    assert child.x is foo_instance

    assert_serializables_equal(roundtrip_func(child), child)


def test_barf_on_unexpected_input():

    class MyClass(Serializable):
        x = Integer()
        # This should be Instance(Foo).
        foo = Foo()

    with pytest.raises(TypeError) as e:
        MyClass(x=1, y=5)
    assert str(e.value) == (
        "MyClass.__init__() got unexpected keyword arguments ('y',)."
    )

    with pytest.raises(TypeError) as e:
        MyClass(x=1, foo=Foo())
    assert str(e.value) == (
        dedent(
            """
            MyClass.__init__() got unexpected keyword argument 'foo'.
            MyClass (or a parent) has a class attribute with the same name.
            Did you mean to write `foo = Instance(Foo)`?
            """
        )
    )


@pytest.fixture
def foo_yaml():
    return dedent(
        """
        bool_: true
        float_: 1.0
        int_: 2
        unicode_: {not_ascii}
        enum: {not_ascii}
        dict_:
            a: 3
            b: 4
            c:
                - 5
                - 6
        list_:
           - 7
           - 8
        set_:
           - 9
           - 10
        tuple_:
           - 11
           - 12
        """
    ).format(not_ascii=not_ascii)


@pytest.fixture
def foo_yaml_expected_result():
    return Foo(
        bool_=True,
        float_=1.0,
        int_=2,
        unicode_=not_ascii,
        enum=not_ascii,
        dict_=dict(
            a=3,
            b=4,
            c=[5, 6],
        ),
        list_=[7, 8],
        set_={9, 10},
        tuple_=(11, 12),
    )


def test_from_yaml(foo_yaml, foo_yaml_expected_result):
    assert_serializables_equal(
        Foo.from_yaml(foo_yaml),
        foo_yaml_expected_result
    )


def test_from_yaml_file(tmpdir, foo_yaml, foo_yaml_expected_result):
    fileobj = tmpdir.join("test.yaml")
    fileobj.write_text(foo_yaml, encoding='utf-8')

    assert_serializables_equal(
        Foo.from_yaml_file(fileobj.strpath),
        foo_yaml_expected_result,
    )


def test_reject_non_serializable_traitlet():

    with pytest.raises(TypeError) as e:
        class F(Serializable):
            u = base_Unicode()
    assert str(e.value) == "Got non-serializable trait u=Unicode"


def test_reject_unknown_object():

    class SomeRandomClass(object):
        pass

    with pytest.raises(TypeError) as e:
        class F(Serializable):
            i = Instance(SomeRandomClass)

    assert str(e.value) == (
        "Can't convert instances of SomeRandomClass to primitives."
    )


def test_allow_none(foo_instance, different_foo_instance, roundtrip_func):

    class MyClass(Serializable):
        required = Instance(Foo)
        explicit_optional = Instance(Foo, allow_none=True)
        implicit_optional = Instance(Foo, allow_none=True, default_value=None)

    with pytest.raises(TraitError):
        MyClass().required

    with pytest.raises(TraitError):
        # This should still raise because there's no default value.
        MyClass().explicit_optional

    assert MyClass().implicit_optional is None

    without_optional = MyClass(required=foo_instance, explicit_optional=None)
    assert without_optional.required is foo_instance
    assert without_optional.explicit_optional is None
    assert_serializables_equal(
        without_optional,
        roundtrip_func(without_optional),
    )

    with_optional = MyClass(
        required=foo_instance,
        explicit_optional=different_foo_instance,
    )
    assert with_optional.required is foo_instance
    assert with_optional.explicit_optional is different_foo_instance
    assert_serializables_equal(
        with_optional,
        roundtrip_func(with_optional),
    )


def test_lazy_attribute_access():

    class MyClass(Serializable):
        x = Integer()

    m = MyClass()
    with pytest.raises(TraitError):
        m.x

    assert MyClass(x=1).x == 1


def test_validate_all_attributes():

    class MyClass(Serializable):
        x = Integer()

    m = MyClass()
    with pytest.raises(TraitError) as validate_err:
        m.validate_all_attributes()

    with pytest.raises(TraitError) as touch_err:
        m.x

    assert str(validate_err.value) == str(touch_err.value)


def test_strict_serializable():

    class Strict(StrictSerializable):
        x = Integer()

    with pytest.raises(TraitError):
        Strict()

    with pytest.raises(TraitError):
        Strict.from_dict({})

    with pytest.raises(TypeError):
        Strict(x=1, y=2)

    assert Strict(x=1).x == 1
    assert Strict(x=1).to_dict() == {"x": 1}


class MultipleErrorsStrict(StrictSerializable):
    """This is not defined in the body of a function because it breaks my regex!
    """
    x = Integer()
    y = Integer()


def test_multiple_trait_errors():

    with pytest.raises(MultipleTraitErrors) as e:
        MultipleErrorsStrict()

    assert re.match(
        dedent(
            """\
            ^
            x: No default value found for x trait of <.+?>
            --------------------
            y: No default value found for y trait of <.+?>$"""
        ),
        str(e.value)
    )
