"""Property support for attrs"""
from functools import partial
import attr

__version__ = "0.0.1"

def property_getter(self, name, getter = None, cache = False):
	"""
	Getter of the property
	@params:
		name (str): The name of the property
		getter (callable): User-defined getter
		cache (bool): Whether cache the results
	"""
	if cache and name in self.__attrs_property_cached__:
		return self.__attrs_property_cached__[name]
	ret = getter(self, self.__attrs_property_raw__[name]) \
		if callable(getter) else self.__attrs_property_raw__[name]
	if cache:
		self.__attrs_property_cached__[name] = ret
	return ret

def property_setter(self, value, name, setter = None, converter = None, validator = None):
	"""
	Setter of the property
	@params:
		value (any): The value of the property
		name (str): The name of the property
		setter (callable): A post user-defined setter
		converter (callable): The converter defined in attr_property
		validator (callable): The validator defined in attr_property
	"""
	# remove the cached value
	if name in self.__attrs_property_cached__:
		del self.__attrs_property_cached__[name]
	if converter:
		value = converter(value)
	if validator:
		validator(self, attr.fields_dict(self.__class__)[name], value)
	self.__attrs_property_raw__[name] = value
	if setter:
		setter(self, value)

def property_deleter(self, name, deleter = None):
	"""
	Deleter of the property
	@params:
		name (str): The name of the property
		deleter (callable): User-defined deleter
	"""
	del self.__attrs_property_raw__[name]
	if name in self.__attrs_property_cached__:
		del self.__attrs_property_cached__[name]
	if deleter:
		deleter(self)

def _attrs_to_init_script(attrs, frozen, slots, post_init, cache_hash, base_attr_map, is_exc):
	"""Used to replace the function in attr._make to create __init__ function"""
	# pragma: no cover
	script, globs, annotations = attr._make._attrs_to_init_script(
		attrs, frozen, slots, post_init, cache_hash, base_attr_map, is_exc
	)
	lines = script.splitlines()
	lines.insert(1, '    self.__attrs_property_cached__ = {}')
	lines.insert(2, '    self.__attrs_property_raw__ = {}')
	return '\n'.join(lines), globs, annotations

def _make_init(cls, attrs, post_init, frozen, slots,
	cache_hash, base_attr_map, is_exc): # pragma: no cover
	# pylint: disable=E,W,R,C
	attrs = [a for a in attrs if a.init or a.default is not attr._make.NOTHING]

	unique_filename = attr._make._generate_unique_filename(cls, "init")

	script, globs, annotations = _attrs_to_init_script(
		attrs, frozen, slots, post_init, cache_hash, base_attr_map, is_exc
	)
	locs = {}
	bytecode = compile(script, unique_filename, "exec")
	attr_dict = dict((a.name, a) for a in attrs)
	globs.update({"NOTHING": attr._make.NOTHING, "attr_dict": attr_dict})

	if frozen is True:
		# Save the lookup overhead in __init__ if we need to circumvent
		# immutability.
		globs["_cached_setattr"] = attr._make.obj_setattr

	eval(bytecode, globs, locs)

	# In order of debuggers like PDB being able to step through the code,
	# we add a fake linecache entry.
	attr._make.linecache.cache[unique_filename] = (
		len(script),
		None,
		script.splitlines(True),
		unique_filename,
	)

	__init__ = locs["__init__"]
	__init__.__annotations__ = annotations

	return __init__

attr._make._make_init = _make_init


def attr_property_class(cls):
	"""
	Extending attr.s with property support
	"""
	if not hasattr(cls, '__attrs_attrs__'):
		raise ValueError("attr_property_class should be a decorator of an attr.s decorated class.")
	for attribute in cls.__attrs_attrs__:
		if attribute.metadata.get('property'):
			attr_getter = partial(property_getter,
				name   = attribute.name,
				getter = attribute.metadata['property.getter'],
				cache  = attribute.metadata['property.cache'])
			attr_setter = partial(property_setter,
				name      = attribute.name,
				setter    = attribute.metadata['property.setter'],
				converter = attribute.converter \
					if attribute.converter and attribute.metadata['property.converter_runtime'] \
					else None,
				validator = attribute.validator \
					if attribute.validator and attribute.metadata['property.validator_runtime'] \
					else None)
			attr_deleter = partial(property_deleter,
				name = attribute.name,
				deleter = attribute.metadata['property.deleter'])
			setattr(cls, attribute.name, property(
				attr_getter,
				attr_setter,
				None if attribute.metadata['property.deleter'] is False else attr_deleter,
				attribute.metadata['property.doc'] or (
					attribute.metadata['property.getter'].__doc__ \
					if attribute.metadata['property.getter'] \
					else "Property {}".format(attribute.name))
			))
			if attribute.metadata['property.raw']:
				setattr(cls, attribute.metadata['property.raw'] + attribute.name, property(
					# pylint: disable=cell-var-from-loop
					lambda self, name = attribute.name: self.__attrs_property_raw__[name]
				))
	return cls

def attr_property(
	default=attr.NOTHING, validator=None, repr=True, cmp=None, hash=None, init=True,
	metadata=None, type=None, converter=None, factory=None, kw_only=False, eq=None, order=None,
	getter=None, setter=None, deleter=None, # property
	validator_runtime=True, converter_runtime=True,
	cache = True, raw = False, doc = None
):
	"""
	Extending attr.ib
	@params:
		...: attr.ib params
		getter (callable|NoneType): User defined getter
		setter (callable|bool|NoneType): User defined setter
			- None: Use default setter
			- False: Disable setter
		deleter: (callable|bool|NoneType): User defined deleter
			- None: Use default deleter
			- False: Disable deleter
		validator_runtime (bool): Run validator in setter
		converter_runtime (bool): Run converter in setter
		cache (bool): Cache the value calculated in getter
		raw (bool|str): Enable a property to get the raw value before being calculated in getter.
			- False: Disable this property
			- True: Use '_' as prefix
			- Otherwise the prefix.
	@returns:
		(attr.ib): attr.ib object with property metadata
	"""
	metadata = metadata or {}
	metadata['property'] = True
	metadata['property.getter'] = getter
	metadata['property.setter'] = setter
	metadata['property.deleter'] = deleter
	metadata['property.validator_runtime'] = validator_runtime
	metadata['property.converter_runtime'] = converter_runtime
	metadata['property.cache'] = cache
	metadata['property.raw'] = '_' if raw is True else raw
	metadata['property.doc'] = doc
	return attr.ib(
		default=default, validator=validator, repr=repr, cmp=cmp, hash=hash,
		init=init, metadata=metadata, type=type, converter=converter,
		factory=factory, kw_only=kw_only, eq=eq, order=order,
	)
