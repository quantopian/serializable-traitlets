"""
Tests for example generation.
"""
from __future__ import unicode_literals
from textwrap import dedent

import pytest
from yaml import safe_load

from traitlets import TraitError

from straitlets.serializable import Serializable
from straitlets.test_utils import assert_serializables_equal, multifixture
from straitlets.traits import (
    Bool,
    Dict,
    Instance,
    Integer,
    Unicode,
)


class Point(Serializable):
    x = Integer().example(100)
    y = Integer().example(101)


class ExampleClass(Serializable):

    bool_tag = Bool().example(True)
    bool_default = Bool(default_value=False)
    bool_both = Bool(default_value=False).example(True)

    int_tag = Integer().example(1)
    int_default = Integer(default_value=2)
    int_both = Integer(default_value=100).example(3)

    dict_tag = Dict().example({'a': 'b'})
    dict_default = Dict(default_value={'c': 'd'})
    dict_both = Dict(default_value={'z': 'z'}).example({'e': 'f', 'g': 'h'})

    instance_tag = Instance(Point).example(Point(x=0, y=1))
    instance_default = Instance(Point, default_value=Point(x=2, y=3))
    instance_both = Instance(Point, default_value=Point(x=4, y=5)).example(
        Point(x=6, y=7),
    )
    # Instance provides a default example if the value is a Serializable
    # that can provide an example.
    instance_neither = Instance(Point)


@pytest.fixture
def expected_instance():
    return ExampleClass(
        bool_tag=True,
        bool_default=False,
        bool_both=True,
        int_tag=1,
        int_default=2,
        int_both=3,
        dict_tag={'a': 'b'},
        dict_default={'c': 'd'},
        dict_both={'e': 'f', 'g': 'h'},
        instance_tag=Point(x=0, y=1),
        instance_default=Point(x=2, y=3),
        instance_both=Point(x=6, y=7),
        instance_neither=Point(x=100, y=101),
    )


@pytest.fixture
def expected_yaml():
    return dedent(
        """
        bool_tag: true
        bool_default: false
        bool_both: true
        int_tag: 1
        int_default: 2
        int_both: 3
        dict_tag:
            a: b
        dict_default:
            c: d
        dict_both:
            e: f
            g: h
        instance_tag:
            x: 0
            y: 1
        instance_default:
            x: 2
            y: 3
        instance_both:
            x: 6
            y: 7
        instance_neither:
            x: 100
            y: 101
        """
    )


@multifixture
def skip_names():
    yield ()
    yield ('bool_tag',)
    yield ('bool_tag', 'int_tag')
    yield ('dict_tag', 'instance_tag', 'instance_neither')
    yield [
        name for name in ExampleClass.class_trait_names()
        if name.endswith('tag')
    ]


def test_example_instance(expected_yaml, expected_instance):
    instance = ExampleClass.example_instance()

    assert_serializables_equal(instance, expected_instance)
    assert_serializables_equal(instance, ExampleClass.from_yaml(expected_yaml))

    assert ExampleClass.example_yaml() == expected_instance.to_yaml()


def test_example_skip_names(expected_instance, skip_names):
    instance = ExampleClass.example_instance(skip=skip_names)
    assert_serializables_equal(instance, expected_instance, skip=skip_names)

    for name in skip_names:
        with pytest.raises(TraitError):
            getattr(instance, name)


def test_write_example_yaml(tmpdir, expected_instance, skip_names):

    path = tmpdir.join("test.yaml").strpath
    ExampleClass.write_example_yaml(path, skip=skip_names)

    from_file = ExampleClass.from_yaml_file(path)
    assert_serializables_equal(
        from_file,
        expected_instance,
        skip=skip_names,
    )

    for name in skip_names:
        with pytest.raises(TraitError):
            getattr(from_file, name)


def test_nested_example():

    class C(Serializable):
        point = Instance(Point)
        unicode_ = Unicode().tag(example='foo')

    class B(Serializable):
        value = Integer().tag(example=ord('b'))
        next_ = Instance(C)

    class A(Serializable):
        value = Integer().tag(example=ord('a'))
        next_ = Instance(B)

    expected = A(
        value=ord('a'),
        next_=B(
            value=ord('b'),
            next_=C(
                point=Point.example_instance(),
                unicode_='foo',
            ),
        ),
    )

    assert_serializables_equal(expected, A.example_instance())


def test_readme_example():

    class Point(Serializable):
        x = Integer().example(0)
        y = Integer().example(0)

    class Vector(Serializable):
        head = Instance(Point)
        tail = Instance(Point).example(Point(x=1, y=3))

    example_yaml = Vector.example_instance().to_yaml()
    expected = {
        "head": {"x": 0, "y": 0},
        "tail": {"x": 1, "y": 3},
    }
    assert safe_load(example_yaml) == expected
