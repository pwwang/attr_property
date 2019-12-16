import attr
from attr_property import attr_property, attr_property_class

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