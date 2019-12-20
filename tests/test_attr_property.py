import pytest
import attr
from attr_property import attr_property, attr_property_class

def c_setter(self, value):
	print('Value {} has been set to property c.'.format(value))

def d_getter(self, value):
	return value * 3

def e_setter(self, value):
	return value * 100

@attr_property_class
@attr.s
class _TestInstance:

	a = attr.ib()
	b = attr_property()
	c = attr_property(setter = c_setter, deleter = lambda this: setattr(this, 'c_deleted', True))
	d = attr_property(getter = d_getter, converter = int, raw = '_')
	e = attr_property(setter = e_setter, init = False, raw = True)

	@d.validator
	def lessthan20(self, attribute, value):
		if value >= 20:
			raise ValueError("d should be less than 20.")


@attr_property_class
@attr.s(slots = True, eq = False)
class _TestSlots:
	a = attr.ib()
	b = attr_property()
	c = attr_property(init = False, repr = False, getter = lambda this, value: 3)

def test_slots():
	inst_slots = _TestSlots(a = 1, b = 2)
	assert inst_slots.a == 1
	assert inst_slots.b == 2
	assert inst_slots.c == 3

def test(capsys):

	inst = _TestInstance(a = 1, b = 2, c = 3, d = '4')
	assert inst.__attrs_property_raw__ == dict(b = 2, c = 3, d = 4)
	assert inst.__attrs_property_cached__ == {'d': 12}
	assert isinstance(inst, _TestInstance)
	assert inst.a == 1
	assert inst.b == 2
	assert inst.c == 3
	assert inst.d == 12
	assert inst._d == 4
	inst.e = 1
	assert inst.e == 100
	assert inst._e == 100
	assert inst.__attrs_property_cached__ == dict(b = 2, c = 3, d = 12, e = 100)

	assert 'Value 3 has been set to property c.' in capsys.readouterr().out
	assert inst.c == 3
	assert inst.c == 3 # cached
	assert not hasattr(inst, 'c_deleted')
	del inst.c
	assert inst.c_deleted
	assert inst.__attrs_property_raw__ == dict(b = 2, d = 4, e = 100)
	assert inst.__attrs_property_cached__ == dict(b = 2, d = 12, e = 100)
	inst.c = 30
	assert 'Value 30 has been set to property c.' in capsys.readouterr().out
	assert inst.c == 30
	inst.c = 300 # cache update
	assert inst.c == 300

def test_exception():
	class B:
		pass
	with pytest.raises(ValueError):
		attr_property_class(B)


