from __future__ import annotations

from typing import Any, Final, NamedTuple
import base64
from collections.abc import Callable, Sequence
import datetime
from enum import Enum
from itertools import chain

__all__ = (
    "AttrField",
    "AttrSpec",
    "BaseExporter",
    "FallbackChain",
    "NormalizedAttr",
)


class FallbackChain(NamedTuple):
    """
    Container for fallback attribute paths.

    Used to specify alternative attribute paths when the first path yields no value.
    For example, if the first path is empty, the next one is tried.

    Attributes
    ----------
    paths: list[tuple[int, str]]
        Fallback attribute paths as `(obj_index, path)` tuples.
    """

    paths: list[tuple[int, str]]


class AttrField:
    """
    Fluent builder for attribute specifications for export.

    Examples
    --------
    Simple attribute:
        >>> AttrField("Name", "naam")

    Auto-label from attribute name:
        >>> AttrField(None, "vestigingsadres.plaats")  # Label becomes "plaats"

    Dotted path:
        >>> AttrField("City", "vestigingsadres.plaats")  # Label is "City"

    Multiple attributes (creates nested dict):
        >>> AttrField("Address").add("straat").add("huisnummer").add("plaats")

    With fallback:
        >>> AttrField("Website", "website").fallback("organisatie.website")
        # Tries "organisatie.website" if "website" is empty

    From specific object:
        >>> AttrField("First").from_obj(0, "naam")

    Multiple objects:
        >>> AttrField("Combined").from_obj(0, "plaats").from_obj(1, "plaats")

    With transformer:
        >>> AttrField("Link").transform(lambda obj: f"https://example.com/{obj.id}")
    """

    __slots__ = ("_auto_label", "_is_fallback", "_paths", "_transformer", "label")

    def __init__(self, label: str | None, path: str | None = None) -> None:
        """
        Create a new attribute specification builder.

        Parameters
        ----------
        label: str | None
            Column label. If None, the label may be inferred from the first
            attribute path added.
        path: str | None
            Optional initial attribute path.
        """
        self.label = label
        self._auto_label = label is None
        self._paths: list[tuple[int, str]] = []
        self._transformer: Callable[[Any], Any] | None = None
        self._is_fallback: bool = False
        if path is not None:
            self._paths.append((0, path))

    def add(self, path: str, obj_index: int = 0) -> AttrField:
        """
        Add an attribute path (defaults to object 0).

        Parameters
        ----------
        path: str
            The attribute path to add (e.g., "naam").
        obj_index: int
            The index of the object to use (default is 0).

        Returns
        -------
        AttrField
            The current AttrField instance (for chaining).
        """
        self._paths.append((obj_index, path))
        return self

    def fallback(self, path: str, obj_index: int = 0) -> AttrField:
        """
        Add a fallback path to try if the previous paths return empty.

        Parameters
        ----------
        path: str
            The fallback attribute path.
        obj_index: int
            The index of the object to use (default is 0).

        Returns
        -------
        AttrField
            The current AttrField instance (for chaining).
        """
        self._paths.append((obj_index, path))
        self._is_fallback = True
        return self

    def transform(self, func: Callable[[Any], Any], /) -> AttrField:
        """
        Add a transformer function to compute the value from the object.

        Parameters
        ----------
        func: Callable[[Any], Any]
            A function that takes the object and returns the transformed value.

        Returns
        -------
        AttrField
            The current AttrField instance (for chaining).
        """
        self._transformer = func
        return self

    def from_obj(self, obj_index: int, path: str) -> AttrField:
        """
        Add an attribute from a specific object.

        Parameters
        ----------
        obj_index: int
            The index of the object to use.
        path: str
            The attribute path to add.

        Returns
        -------
        AttrField
            The current AttrField instance (for chaining).
        """
        self._paths.append((obj_index, path))
        return self

    def to_spec(self) -> tuple[str, list[tuple[int, str]] | Callable[[Any], Any] | FallbackChain]:
        """
        Convert to internal normalized format for use by exporters.

        Returns
        -------
        tuple[str, list[tuple[int, str]] | Callable[[Any], Any] | FallbackChain]
            The label and the attribute specification (paths, transformer, or fallback chain).
        """
        label = self.label
        if self._auto_label and self._paths:
            # Use last segment of first path as label
            _, first_path = self._paths[0]
            label = first_path.split(".")[-1]

        # If transformer is set, use it instead of paths
        if self._transformer is not None:
            return (label or "value", self._transformer)

        if self._is_fallback:
            return (label or "value", FallbackChain(self._paths))

        return (label or "value", self._paths)


AttrSpec = str | tuple[str, str | Sequence[str] | Sequence[tuple[int, str]]] | AttrField
NormalizedAttr = tuple[str, list[tuple[int, str]] | Callable[[Any], Any] | FallbackChain]


def _get_all_slots(cls: type) -> frozenset[str]:
    """
    Collect all `__slots__` entries from a class hierarchy.

    Parameters
    ----------
    cls: type
        Class to collect slots for.

    Returns
    -------
    frozenset[str]
        A set of all slot names found in `cls.__mro__`.
    """

    slot_iterables = (getattr(klass, "__slots__", ()) for klass in cls.__mro__)
    return frozenset(chain.from_iterable(slot_iterables))


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

    def _get_slots_cached(self, cls: type) -> frozenset[str]:
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
        if cls not in self._slots_cache:
            self._slots_cache[cls] = _get_all_slots(cls)
        return self._slots_cache[cls]

    def _should_include(self, value: Any) -> bool:
        """
        Determine if a value should be included in the export, based on the include_empty flag.

        Parameters
        ----------
        value: Any
            The value to check.

        Returns
        -------
        bool
            True if the value should be included, False otherwise.
        """
        if self._include_empty:
            return True
        return not self._is_empty(value)

    @staticmethod
    def _is_empty(value: Any) -> bool:
        """
        Check if a value is considered empty.

        Parameters
        ----------
        value: Any
            The value to check.

        Returns
        -------
        bool
            True if the value is empty, False otherwise.
        """
        if value is None or value is False:
            return True
        if isinstance(value, (str, list, dict, tuple, set, frozenset)):
            return len(value) == 0
        return bool(isinstance(value, (int, float)) and value == 0)

    def _resolve_attribute(self, obj: Any, attr: str) -> Any:
        """
        Resolve a (possibly nested) attribute from an object.

        Works with nested paths like "organisatie.email" or simple attributes like "naam".
        Returns None if any part of the path is missing or None.
        This avoids exceptions and enables fallback logic.

        Parameters
        ----------
        obj: Any
            The object to resolve the attribute from.
        attr: str
            Dotted path, e.g., "organisatie.email".

        Returns
        -------
        Any
            The resolved value, or None if any part is missing.
        """
        if "." in attr:
            parts = attr.split(".")
            current = obj
            for part in parts:
                if current is None:
                    return None
                try:
                    current = getattr(current, part)
                except AttributeError:
                    return None
            return current
        return getattr(obj, attr, None)

    @staticmethod
    def _get_attr_key(path: str) -> str:
        """
        Extract the final attribute name from a dotted path.

        Parameters
        ----------
        path: str
            The dotted attribute path (e.g., "organisatie.email").

        Returns
        -------
        str
            The last segment of the path (e.g., "email").
        """
        return path.rsplit(".", maxsplit=1)[-1]

    @staticmethod
    def _normalize_attrs(attrs: Sequence[AttrSpec]) -> list[NormalizedAttr]:
        """
        Normalize attribute specifications to (label, [(obj_idx, path), ...]).

        Supports strings, tuples, and AttrField instances.

        Parameters
        ----------
        attrs: Sequence[AttrSpec]
            The attribute specifications to normalize.

        Returns
        -------
        list[NormalizedAttr]
            The normalized attribute specifications.
        """
        normalized: list[NormalizedAttr] = []
        for spec in attrs:
            # Handle AttrField instances
            if isinstance(spec, AttrField):
                normalized.append(spec.to_spec())
                continue

            if isinstance(spec, tuple):
                label, paths = spec
            else:
                label, paths = spec, spec

            # Handle callable transformer
            if callable(paths):
                normalized.append((label, paths))  # Store as-is for later processing
                continue

            # Convert to list of (obj_index, path) tuples
            path_list: list[tuple[int, str]] = []
            if isinstance(paths, str):
                path_list = [(0, paths)]
            elif isinstance(paths, Sequence):
                for item in paths:
                    if isinstance(item, tuple) and len(item) == 2:
                        path_list.append(item)
                    elif isinstance(item, str):
                        # Default to first object (index 0)
                        path_list.append((0, item))
                    else:
                        path_list.append((0, str(item)))

            normalized.append((label, path_list))
        return normalized

    def _convert_enum(self, obj: Enum) -> Any:
        """
        Convert an Enum to its value.

        Parameters
        ----------
        obj: Enum
            The Enum instance to convert.

        Returns
        -------
        Any
            The value of the Enum.
        """
        return obj.value

    def _convert_datetime(self, obj: datetime.datetime | datetime.date | datetime.time) -> str:
        """
        Convert a datetime, date, or time object to an ISO 8601 string.

        Parameters
        ----------
        obj: datetime.datetime | datetime.date | datetime.time
            The object to convert.

        Returns
        -------
        str
            The ISO 8601 string representation.
        """
        return obj.isoformat()

    def _convert_timedelta(self, obj: datetime.timedelta) -> float:
        """
        Convert a timedelta to the number of seconds (float).

        Parameters
        ----------
        obj: datetime.timedelta
            The timedelta object to convert.

        Returns
        -------
        float
            The total number of seconds.
        """
        return obj.total_seconds()

    def _convert_bytes(self, obj: bytes | bytearray) -> str:
        """
        Convert bytes or bytearray to a string.
        Tries UTF-8 first, otherwise base64-encodes.

        Parameters
        ----------
        obj: bytes | bytearray
            The bytes or bytearray to convert.

        Returns
        -------
        str
            The decoded string (UTF-8 or base64).
        """
        try:
            return obj.decode("utf-8")
        except UnicodeDecodeError:
            return base64.b64encode(obj).decode("ascii")
