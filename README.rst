======================
serializable-traitlets
======================
Serializable IPython Traitlets

``serializable-traitlets`` (imported as ``straitlets``) is a Python 2/3
compatible library providing a restricted subset of the classes from `IPython
Traitlets`_.  Within our restricted subset, we inherit all the benefits of
using regular ``traitlets``, including static type declarations, `dynamic
default generators`_, and `attribute observers/validators`_.

By supporting only a limited (though still expressive) subset of Python
objects, however, we gain the ability to serialize and deserialize instances of
``Serializable`` to and from various formats, including:

#. JSON
#. YAML
#. base64-encoded strings

These properties make ``Serializables`` well-suited for configuration in
environments where objects need to be transferred between processes.

``straitlets`` also provides users the ability to specify ``example`` values
for traits.  If all traits of a ``Serializable`` class have examples (or
default values) provided, then we can auto-generate an example for the parent
class, and we can resursively generate examples for nested classes.

Usage
-----

**Basic Usage:**

.. code-block:: python

   In [1]: from straitlets import Serializable, Integer, Dict, List
   In [2]: class Foo(Serializable):
      ...:     my_int = Integer()
      ...:     my_dict = Dict()
      ...:     my_list = List()

   In [3]: instance = Foo(my_int=3, my_dict={'a': [1, 2], 'b': (3, 4)}, my_list=[5, None])

   In [4]: print(instance.to_json())
   {"my_int": 3, "my_dict": {"a": [1, 2], "b": [3, 4]}, "my_list": [5, null]}

   In [5]: print(instance.to_yaml())
   my_dict:
   a:
   - 1
   - 2
   b:
   - 3
   - 4
   my_int: 3
   my_list:
   - 5
   - null

**Autogenerating Example Values:**

.. code-block:: python

   from straitlets import Serializable, Integer, Instance

   class Point(Serializable):
       x = Integer().example(0)
       y = Integer().example(0)


   class Vector(Serializable):
       # We can automatically generate example values for attributes
       # declared as Instances of Serializable.
       head = Instance(Point)

       # Per-attribute overrides are still supported.
       tail = Instance(Point).example(Point(x=1, y=3))

   print(Vector.example_instance().to_yaml())
   # head:
   #   x: 0
   #   y: 0
   # tail:
   #   x: 1
   #   y: 3

.. _`IPython Traitlets` : http://traitlets.readthedocs.org
.. _`dynamic default generators` : http://traitlets.readthedocs.org/en/stable/using_traitlets.html#dynamic-default-values
.. _`attribute observers/validators` : http://traitlets.readthedocs.org/en/stable/using_traitlets.html#callbacks-when-trait-attributes-change
