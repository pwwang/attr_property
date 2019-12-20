
attr_property
=============

`
.. image:: https://img.shields.io/pypi/v/attr_property?style=flat-square
   :target: https://img.shields.io/pypi/v/attr_property?style=flat-square
   :alt: Pypi
 <https://pypi.org/project/attr_property/>`_ `
.. image:: https://img.shields.io/github/tag/pwwang/attr_property?style=flat-square
   :target: https://img.shields.io/github/tag/pwwang/attr_property?style=flat-square
   :alt: Github
 <https://github.com/pwwang/attr_property>`_ `
.. image:: https://img.shields.io/pypi/pyversions/attr_property?style=flat-square
   :target: https://img.shields.io/pypi/pyversions/attr_property?style=flat-square
   :alt: PythonVers
 <https://pypi.org/project/attr_property/>`_ `
.. image:: https://img.shields.io/travis/pwwang/attr_property?style=flat-square
   :target: https://img.shields.io/travis/pwwang/attr_property?style=flat-square
   :alt: Travis building
 <https://travis-ci.org/pwwang/attr_property>`_ `
.. image:: https://img.shields.io/codacy/grade/41140ad263bc435a822777bed8a41b8d?style=flat-square
   :target: https://img.shields.io/codacy/grade/41140ad263bc435a822777bed8a41b8d?style=flat-square
   :alt: Codacy
 <https://app.codacy.com/manual/pwwang/attr_property/dashboard>`_ `
.. image:: https://img.shields.io/codacy/coverage/41140ad263bc435a822777bed8a41b8d?style=flat-square
   :target: https://img.shields.io/codacy/coverage/41140ad263bc435a822777bed8a41b8d?style=flat-square
   :alt: Codacy coverage
 <https://app.codacy.com/manual/pwwang/attr_property/dashboard>`_

Property support for attrs

Installation
------------

.. code-block:: shell

   pip install attr_property

Usage
-----

Definitaion of class with ``attr_property``\ s
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import attr
   from attr_property import attr_property, attr_property_class

   @attr_property_class
   @attr.s
   class A:

     a = attr_property()
     b = attr.ib() # compatible with original attr.ib

Specification of getter, setter, and deleter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def a_getter(this, value):
       print('Property a has been accessed!')
       return value + 1
   def a_setter(this, value):
       print(f'Property a has been set with value {value!r}')
   def a_deleter(this):
       print('Property has been deleted!')

   @attr_property_class
   @attr.s
   class A:
       a = attr_property(getter = a_getter, setter = a_setter, deleter = a_deleter)

   a = A(a = 1)
   # Property a has been set with value 1
   # Property a has been accessed!
   print('a.a =', a.a)
   # a.a = 2
   del a.a
   # Property has been deleted!
   a.a
   # Error

Disabling deleter
^^^^^^^^^^^^^^^^^

.. code-block:: python

   @attr_property_class
   @attr.s
   class A:
       a = attr_property(deleter = False)

   a = A(1)
   del a.a
   # AttributeError: can't delete attribute

Disabling setter
^^^^^^^^^^^^^^^^

.. code-block:: python

   @attr_property_class
   @attr.s
   class A:
       # remember you can set init = True or
       # set any default values for it,
       # as setter will be called in __init__
       # this will cause AttributeError
       a = attr_property(init = False, setter = False, getter = lambda this, value: 2)

   a = A()
   a.a = 1
   # AttributeError: can't set attribute

   # OK to call getter
   a.a == 2

Run ``attr.ib``\ 's converter and validator in setter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   @attr_property_class
   @attr.s
   class A:
       a = attr_property(converter = int, validator_runtime = True, converter_runtime = True)

       @a.validator
       def lessthan20(self, attribute, value):
           if value >= 20:
               raise ValueError("d should be less than 20.")

   a = A('3')
   # a.a == 3
   a.a = '30'
   # ValueError

Order of execution of setter:


* Delete cached value
* Run converter
* Run validator
* Run specified setter
* Save value as raw value

Caching getter results
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   @attr_property_class
   @attr.s
   class A:
       a = attr_property(getter = lambda this, value: value + 1, cache = True)

   a = A(1)
   # a.a == 2
   # will not do value + again
   # validators and converters will be skipped, as well.

Accessing raw values before getter calculation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   @attr_property_class
   @attr.s
   class A:
       a = attr_property(getter = lambda this, value: value + 1, convert  = int, raw = True)

   a = A('1')
   # a.a == 2
   # a._a == 1 # converted value
   a._a = 9
   # AttributeError, it's readonly

Using a different prefix

.. code-block:: python

   @attr_property_class
   @attr.s
   class A:
       a = attr_property(getter = lambda this, value: value + 1, convert  = int, raw = 'raw_')

   a = A('1')
   # a.raw_a == 1

How does it work?
-----------------


* Hack attrs' ``_attrs_to_init_script`` function to insert codes to initiate ``self.__attrs_property_raw__`` to save raw values and ``__attrs_property_cached__`` to save cached values.
* Create ``property``\ s for each attribute in class decorator ``attr_property_class``.
