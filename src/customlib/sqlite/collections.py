# -*- coding: UTF-8 -*-

from typing import Mapping, TypeVar, Union, Iterable

from .exceptions import KeyNotFoundError, DuplicateKeyError
from .utils import single_quote

Key = TypeVar("Key")
Value = TypeVar("Value")


class Collection(dict):
    """
    A container class used for storing `ORM` specific objects.

    This class kept all of :class:`dict` core functionality except for:
        :func:`__iter__`
            It iterates through `values` instead of `keys`.

        :func:`__repr__`
            It represents it's `key`, `value` pairs like a :func:`namedtuple`
            instance.

    Attributes can also be assigned, retrieved and deleted just as with any
    :class:`object` instance.

    ----

    Example:

        - ``test.insert({"last_name": "Doe"})``
        - ``test.insert(age=54)``
        - ``test.insert((("year", 1984), ("salary", 3500)))``
        - ``del test.salary``

    ----

    It will raise:
        :class:`DuplicateKeyError` for existing keys;
        :class:`KeyNotFoundError` for missing keys.
    """

    def insert(self, mapping: Union[Mapping[Key, Value], Iterable[Iterable]] = None, **kwargs):
        """

        As with :func:`update()`, insert `key`-`value` pairs into :class:`Collection` using the
        :func:`__setattr__` method.

        It will check for duplicate keys and raise a :class:`DuplicateKeyError`
        if found.

        :param mapping: Another dict, an object with a `key` attribute or a
            `key-value` pair iterable.
        :param kwargs: Keyword arguments.
        :raise DuplicateKeyError: For existing keys.
        """
        if mapping is not None:
            if hasattr(mapping, "keys"):
                for key in mapping:
                    self.__setattr__(key, mapping[key])
            else:
                for key, value in mapping:
                    self.__setattr__(key, value)
        if kwargs:
            for key in kwargs:
                self.__setattr__(key, kwargs[key])

    def __getattr__(self, item):
        """
        Fetch `item` attribute.

        :param item: The name of the attribute.
        :raise KeyNotFoundError: If the key does not exist.
        """
        if item not in self.keys():
            raise KeyNotFoundError(f"No such key '{item}' in '{self.__class__.__name__}' collection.")
        return self.__getitem__(item)

    def __setattr__(self, key, value):
        """
        Add a new `key`, `value` pair.

        :param key: The name of the attribute.
        :param value: The attribute value.
        :raise DuplicateKeyError: For existing keys.
        """
        if key in self.keys():
            raise DuplicateKeyError(f"Duplicate key '{key}' in '{self.__class__.__name__}' collection.")
        self.__setitem__(key, value)

    def __delattr__(self, item):
        """
        Delete `item` attribute.

        :param item: The name of the attribute.
        :raise KeyNotFoundError: If the key does not exist.
        """
        if item not in self.keys():
            raise KeyNotFoundError(f"No such key '{item}' in '{self.__class__.__name__}' collection.")
        self.__delitem__(item)

    def __iter__(self):
        """Iterate through the collection values."""
        return iter(self.values())

    def __repr__(self):
        fields = tuple(
            f"{key}={single_quote(value)}"
            for key, value in self.items()
        )
        return f"{self.__class__.__name__}({', '.join(fields)})"


class Tables(Collection):
    """Container for tables."""


class Columns(Collection):
    """Container for columns."""


class Indexes(Collection):
    """Container for indexes."""


class Views(Collection):
    """Container for views."""


class Triggers(Collection):
    """Container for triggers."""
