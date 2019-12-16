# attr_property

[![Pypi][3]][4] [![Github][5]][6] [![PythonVers][8]][4] [![Travis building][10]][11] [![Codacy][12]][13] [![Codacy coverage][14]][13]

Property support for attrs

## Installation
```shell
pip install attr_property
```

## Usage
### Definitaion of class with `attr_property`s
```python
import attr
from attr_property import attr_property, attr_property_class

@attr_property_class
@attr.s
class A:

  a = attr_property()
  b = attr.ib() # compatible with original attr.ib
```

### Specification of getter, setter, and deleter
```python
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
```

### Disabling deleter

```python
@attr_property_class
@attr.s
class A:
    a = attr_property(deleter = False)

a = A(1)
del a.a
# AttributeError: can't delete attribute
```

### Run `attr.ib`'s converter and validator in setter

```python
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
```

Order of execution of setter:

- Delete cached value
- Run converter
- Run validator
- Save converted value as raw value
- Run specified setter

### Caching getter results

```python
@attr_property_class
@attr.s
class A:
    a = attr_property(getter = lambda this, value: value + 1, cache = True)

a = A(1)
# a.a == 2
# will not do value + again
# validators and converters will be skipped, as well.
```

### Accessing raw values before getter calculation

```python
@attr_property_class
@attr.s
class A:
    a = attr_property(getter = lambda this, value: value + 1, convert  = int, raw = True)

a = A('1')
# a.a == 2
# a._a == 1 # converted value
a._a = 9
# AttributeError, it's readonly
```

Using a different prefix
```python
@attr_property_class
@attr.s
class A:
    a = attr_property(getter = lambda this, value: value + 1, convert  = int, raw = 'raw_')

a = A('1')
# a.raw_a == 1
```

## How does it work?

- Hack attrs' `_attrs_to_init_script` function to insert codes to initiate `self.__attrs_property_raw__` to save raw values and `__attrs_property_cached__` to save cached values.
- Create `property`s for each attribute in class decorator `attr_property_class`.

[1]: https://github.com/pwwang/attr_property
[3]: https://img.shields.io/pypi/v/attr_property?style=flat-square
[4]: https://pypi.org/project/attr_property/
[5]: https://img.shields.io/github/tag/pwwang/attr_property?style=flat-square
[6]: https://github.com/pwwang/attr_property
[8]: https://img.shields.io/pypi/pyversions/attr_property?style=flat-square
[10]: https://img.shields.io/travis/pwwang/attr_property?style=flat-square
[11]: https://travis-ci.org/pwwang/attr_property
[12]: https://img.shields.io/codacy/grade/41140ad263bc435a822777bed8a41b8d?style=flat-square
[13]: https://app.codacy.com/manual/pwwang/attr_property/dashboard
[14]: https://img.shields.io/codacy/coverage/41140ad263bc435a822777bed8a41b8d?style=flat-square
