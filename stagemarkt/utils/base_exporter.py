from __future__ import annotations

from typing import Any, Final, NamedTuple
from collections.abc import Callable, Iterable, Sequence
import datetime
from itertools import chain

__all__ = (
    "AttrField",
    "AttrSpec",
    "BaseExporter",
    "FallbackChain",
    "NormalizedAttr",
    "SortSpec",
    "sort_on",
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

    A flexible builder for defining how to extract and transform data from objects
    during export operations. Supports simple attributes, nested paths, fallbacks,
    multi-object access, and custom transformations.

    Examples
    --------
    Simple attribute extraction:
        >>> AttrField(label="Name", path="naam")
        >>> AttrField(label="Email", path="email")

    Auto-label from attribute name (label inferred from last path segment):
        >>> AttrField(path="vestigingsadres.plaats")  # Label becomes "plaats"
        >>> AttrField(path="organisatie.email")  # Label becomes "email"

    Dotted path for nested attributes:
        >>> AttrField(label="City", path="vestigingsadres.plaats")
        >>> AttrField(label="Street", path="address.straat")

    Multiple attributes (combines into nested dict):
        >>> AttrField(label="Address").add(path="straat").add(path="huisnummer").add(path="plaats")
        # Result: {"straat": "...", "huisnummer": "...", "plaats": "..."}

    Fallback paths (tries alternatives if previous is empty):
        # Tries "website" first, then "organisatie.website" if empty
        >>> AttrField(label="Website", path="website").fallback("organisatie.website")
        # Tries "phone" first, then "organisatie.phone", then "contact.phone" if empty
        >>> AttrField(label="Phone").add(path="phone").fallback("organisatie.phone").fallback("contact.phone")

    From specific object (for multi-object scenarios):
        >>> AttrField(label="First Name").from_obj(0, "naam")
        >>> AttrField(label="Second Name").from_obj(1, "naam")

    Combining multiple objects:
        >>> AttrField(label="Cities").from_obj(0, "plaats").from_obj(1, "plaats")
        # Result: {"plaats": "Amsterdam", "plaats": "Rotterdam"}

    Custom transformer function:
        >>> AttrField(label="Link").transform(lambda obj: f"https://example.com/{obj.id}")
        >>> AttrField(label="Full Name").transform(lambda obj: f"{obj.first_name} {obj.last_name}")
        >>> AttrField(label="Date").transform(lambda obj: obj.created_at.strftime("%Y-%m-%d"))

    Complex example combining multiple features:
        >>> (AttrField(label="Organization")
        ...  .add(path="naam")
        ...  .add(path="kvk_nummer")
        ...  .fallback("registration.kvk"))
    """

    __slots__ = ("_is_fallback", "_paths", "_transformer", "label")

    def __init__(self, *, label: str | None = None, path: str | None = None) -> None:
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
        self.label: str | None = label
        self._paths: list[tuple[int, str]] = []
        self._transformer: Callable[[Any], Any] | None = None
        self._is_fallback: bool = False
        if path is not None:
            self.add(path=path)

    def add(self, *, path: str, obj_index: int = 0) -> AttrField:
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
        self.add(path=path, obj_index=obj_index)
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
        self.add(path=path, obj_index=obj_index)
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
        if not label and self._paths:
            _, first_path = self._paths[0]
            label = first_path.split(".")[-1]

        if self._transformer is not None:
            return (label or "value", self._transformer)

        if self._is_fallback:
            return (label or "value", FallbackChain(self._paths))

        return (label or "value", self._paths)


AttrSpec = str | tuple[str, str | Sequence[str] | Sequence[tuple[int, str]]] | AttrField
NormalizedAttr = tuple[str, list[tuple[int, str]] | Callable[[Any], Any] | FallbackChain]
SortSpec = tuple[int, str] | tuple[str] | str


def sort_on(path: str, obj_index: int = 0) -> SortSpec:
    """Build a sort spec with an object index and attribute path."""
    return (obj_index, path)


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

    def _iter_attr_values(
        self,
        obj: Any,
        attrs: Sequence[AttrSpec],
        objects: Sequence[Any] | None = None,
        *,
        convert: Callable[[Any], Any] | None = None,
    ) -> Iterable[tuple[str, Any]]:
        """
        Iterate over normalized attributes and yield (label, value).

        Parameters
        ----------
        obj: Any
            Primary object to read values from.
        attrs: Sequence[AttrSpec]
            Attribute specifications.
        objects: Sequence[Any] | None
            Additional objects for multi-object attribute access.
        convert: Callable[[Any], Any] | None
            Conversion function applied to extracted values.

        Yields
        ------
        Iterable[tuple[str, Any]]
            (label, converted value) pairs.
        """
        normalized = self._normalize_attrs(attrs)
        yield from self._iter_normalized_values(obj, normalized, objects, convert=convert)

    def _iter_normalized_values(
        self,
        obj: Any,
        normalized_attrs: Sequence[NormalizedAttr],
        objects: Sequence[Any] | None = None,
        *,
        convert: Callable[[Any], Any] | None = None,
    ) -> Iterable[tuple[str, Any]]:
        """
        Iterate over pre-normalized attributes and yield (label, value).

        Parameters
        ----------
        obj: Any
            Primary object to read values from.
        normalized_attrs: Sequence[NormalizedAttr]
            Normalized attribute specifications.
        objects: Sequence[Any] | None
            Additional objects for multi-object attribute access.
        convert: Callable[[Any], Any] | None
            Conversion function applied to extracted values.

        Yields
        ------
        Iterable[tuple[str, Any]]
            (label, converted value) pairs.
        """
        all_objects = [obj] if objects is None else list(objects)

        convert = convert or (lambda v: v)

        for label, indexed_paths in normalized_attrs:
            if callable(indexed_paths):
                try:
                    value = convert(indexed_paths(obj))
                except Exception:  # noqa: BLE001
                    value = None
                yield label, value
                continue

            if isinstance(indexed_paths, FallbackChain):
                value = None
                for obj_idx, path in indexed_paths.paths:
                    target_obj = all_objects[obj_idx] if obj_idx < len(all_objects) else obj
                    value = convert(self._resolve_attribute(target_obj, path))
                    if not self._is_empty(value):
                        break
                yield label, value
                continue

            if len(indexed_paths) == 1:
                obj_idx, path = indexed_paths[0]
                target_obj = all_objects[obj_idx] if obj_idx < len(all_objects) else obj
                yield label, convert(self._resolve_attribute(target_obj, path))
                continue

            combined: dict[str, Any] = {}
            for obj_idx, path in indexed_paths:
                target_obj = all_objects[obj_idx] if obj_idx < len(all_objects) else obj
                key = self._get_attr_key(path)
                combined[key] = convert(self._resolve_attribute(target_obj, path))
            yield label, combined

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
            value = self._resolve_attribute(target, path[0] if isinstance(path, (list, tuple)) else path)
            return (value is None, value)

        try:
            return sorted(objects, key=key_fn)
        except TypeError:
            return sorted(objects, key=lambda item: str(key_fn(item)))
