from __future__ import annotations

from typing import Any, Final
from collections.abc import Sequence
import datetime
from itertools import chain
from operator import attrgetter

__all__ = (
    "BaseExporter",
    "SortSpec",
)
SortSpec = tuple[int, str] | tuple[str] | str


class BaseExporter:
    """
    Base class with shared helpers for exporter implementations.

    Provides methods for normalizing attributes, resolving nested attributes,
    and converting common data types such as enums, datetimes, and bytes.
    Subclasses can use these helpers to provide consistent export functionality
    to various file formats (such as Excel or JSON).
    """

    __slots__ = ("_include_empty", "_slots_cache")

    _PRIMITIVES: Final[tuple[type, ...]] = (str, int, float, bool, type(None))
    _DATETIME_TYPES: Final[tuple[type, ...]] = (
        datetime.datetime,
        datetime.date,
        datetime.time,
    )
    _BYTES_TYPES: Final[tuple[type, ...]] = (bytes, bytearray)

    def __init__(self, *, include_empty: bool = True) -> None:
        """
        Initialize the exporter base.

        Parameters
        ----------
        include_empty: bool
            If True, include empty values (None, empty strings, empty
            containers) in the export output. Defaults to True.
        """
        self._include_empty = include_empty
        self._slots_cache: dict[type, frozenset[str]] = {}

    def _get_slots(self, cls: type) -> frozenset[str]:
        """
        Get all __slots__ entries for a class, using a cache for efficiency.

        Parameters
        ----------
        cls: type
            The class to get slots for.

        Returns
        -------
        frozenset[str]
            The set of slot names for the class.
        """
        slots = self._slots_cache.get(cls)
        if not slots:
            slot_iterables = (getattr(klass, "__slots__", ()) for klass in cls.__mro__)
            slots = self._slots_cache[cls] = frozenset(chain.from_iterable(slot_iterables))
        return slots

    def _sort_objects(self, objects: Sequence[Any], sort: SortSpec | None) -> list[Any]:
        """
        Sort objects by an attribute path on a specific object index.

        Parameters
        ----------
        objects: Sequence[Any]
            Objects to sort.
        sort: SortSpec | None
            Can be one of the following:

            - (obj_index, path)
            - (path,)
            - path

        Returns
        -------
        list[Any]
            Sorted list of objects.
        """
        if sort is None:
            return list(objects)

        obj_index, path = sort if isinstance(sort, tuple) and len(sort) == 2 else (0, sort)

        def key_fn(item: Any) -> Any:
            target = item
            if isinstance(item, (list, tuple)) and obj_index < len(item):
                target = item[obj_index]
            attr = path[0] if isinstance(path, (list, tuple)) else path
            try:
                value = attrgetter(attr)(target)
            except Exception:  # noqa: BLE001
                value = None
            return (value is None, value)

        try:
            return sorted(objects, key=key_fn)
        except TypeError:
            return sorted(objects, key=lambda item: str(key_fn(item)))
