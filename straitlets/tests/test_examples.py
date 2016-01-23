"""
Tests for example generation.
"""
from __future__ import unicode_literals
from textwrap import dedent
import pytest

from straitlets.serializable import Serializable
from straitlets.test_utils import assert_serializables_equal
from straitlets.traits import (
    Bool,
    Dict,
    Enum,
    Float,
    Instance,
    Integer,
    List,
    Set,
    Tuple,
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


def test_example_instance(expected_yaml, expected_instance):
    instance = ExampleClass.example_instance()

    assert_serializables_equal(instance, expected_instance)
    assert_serializables_equal(instance, ExampleClass.from_yaml(expected_yaml))

    assert ExampleClass.example_yaml() == expected_instance.to_yaml()


def test_write_example_yaml(tmpdir, expected_instance):

    path = tmpdir.join("test.yaml").strpath
    ExampleClass.write_example_yaml(path)

    assert_serializables_equal(
        ExampleClass.from_yaml_file(path),
        expected_instance,
    )


def test_nested_example():

    class C(Serializable):
        point = Instance(Point)
        unicode_ = Unicode(example='foo')

    class B(Serializable):
        value = Integer(example=ord('b'))
        next_ = Instance(C)

    class A(Serializable):
        value = Integer(example=ord('a'))
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
