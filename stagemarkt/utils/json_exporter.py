from __future__ import annotations

from typing import TYPE_CHECKING, Any
from collections.abc import Iterable, Mapping, Sequence
import dataclasses
import datetime
from enum import Enum
from itertools import filterfalse
import json
from pathlib import Path

from .base_exporter import AttrSpec, BaseExporter, FallbackChain

if TYPE_CHECKING:
    from _typeshed import SupportsWrite

__all__ = ("JSONExporter", "to_json")

# Type aliases for clarity
type JSONPrimitive = str | int | float | bool | None
type JSONValue = JSONPrimitive | dict[str, Any] | list[Any]


class JSONExporter(BaseExporter):
    """
    High-performance JSON exporter for Python objects.

    Uses Python standard library for efficient serialization while supporting
    complex objects (dataclasses, mappings, iterables, slotted objects, and
    attribute-based extraction).

    Parameters
    ----------
    include_empty: bool
        If True, include empty values (None, empty strings, empty containers)
        in the output. Defaults to True.
    indent: int | None
        Indentation level for pretty-printed JSON. If None, output is compact.
        Defaults to 4.
    ensure_ascii: bool
        If True, escape non-ASCII characters. Defaults to False.
    """

    __slots__ = ("_ensure_ascii", "_indent")

    def __init__(
        self,
        *,
        include_empty: bool = True,
        indent: int | None = 4,
        ensure_ascii: bool = False,
    ) -> None:
        super().__init__(include_empty=include_empty)
        self._indent: int | None = indent
        self._ensure_ascii: bool = ensure_ascii

    def export(
        self,
        path: Path,
        objects: Sequence[object],
        *,
        root_key: str | None = None,
        attrs: list[AttrSpec] | None = None,
    ) -> None:
        """
        Export objects to a JSON file.

        Parameters
        ----------
        path: Path
            Output file path.
        objects: Sequence[object]
            Sequence of objects to serialize.
        root_key: str | None
            Optional root key to wrap the serialized list. If provided, the
            output becomes a dict with the list under `root_key`.
        attrs: list[AttrSpec] | None
            Attribute specifications to extract. If None, objects are
            converted using generic rules.

        Returns
        -------
        None
            Writes the JSON to `path`.
        """
        data = self._build_output(objects, root_key, attrs)
        with path.open("w", encoding="utf-8") as f:
            self._dump(data, f)

    def dump(
        self,
        objects: Sequence[object],
        fp: SupportsWrite[str],
        *,
        root_key: str | None = None,
        attrs: list[AttrSpec] | None = None,
    ) -> None:
        """
        Serialize objects to a file-like object.

        Parameters
        ----------
        objects: Sequence[object]
            Sequence of objects to serialize.
        fp: SupportsWrite[str]
            A file-like object with a `.write(str)` method.
        root_key: str | None
            Optional root key to wrap the serialized list.
        attrs: list[AttrSpec] | None
            Attribute specifications to extract.

        Returns
        -------
        None
            Writes JSON content to `fp`.
        """
        data = self._build_output(objects, root_key, attrs)
        self._dump(data, fp)

    def dumps(
        self,
        objects: Sequence[object],
        *,
        root_key: str | None = None,
        attrs: list[AttrSpec] | None = None,
    ) -> str:
        """
        Serialize objects to a JSON string.

        Parameters
        ----------
        objects: Sequence[object]
            Sequence of objects to serialize.
        root_key: str | None
            Optional root key to wrap the serialized list.
        attrs: list[AttrSpec] | None
            Attribute specifications to extract.

        Returns
        -------
        str
            The JSON string.
        """
        data = self._build_output(objects, root_key, attrs)
        return json.dumps(
            data,
            ensure_ascii=self._ensure_ascii,
            indent=self._indent,
        )

    def serialize(self, obj: Any, attrs: list[AttrSpec] | None = None, objects: Sequence[Any] | None = None) -> JSONValue:
        """
        Serialize a single object to a JSON-compatible value.

        Parameters
        ----------
        obj: Any
            The object to serialize.
        attrs: list[AttrSpec] | None
            Attribute specifications to extract for `obj`.
        objects: Sequence[Any] | None
            Additional objects for multi-object attribute access.

        Returns
        -------
        JSONValue
            A JSON-compatible value (primitive, dict, or list).
        """
        return self._convert(obj, attrs, objects)

    def _build_output(
        self,
        objects: Sequence[object],
        root_key: str | None,
        attrs: list[AttrSpec] | None,
    ) -> JSONValue:
        """
        Build the final JSON structure.

        Parameters
        ----------
        objects: Sequence[object]
            Objects to serialize.
        root_key: str | None
            Optional root key to wrap the serialized list.
        attrs: list[AttrSpec] | None
            Attribute specifications to extract.

        Returns
        -------
        JSONValue
            Either a list of items or a dict with `root_key`.
        """
        items = [self._convert(obj, attrs) for obj in objects]
        return {root_key: items} if root_key else items

    def _dump(self, data: JSONValue, fp: SupportsWrite[str]) -> None:
        """
        Write JSON to file-like object with configured options.

        Parameters
        ----------
        data: JSONValue
            The JSON-compatible data to write.
        fp: SupportsWrite[str]
            A file-like object with a `.write(str)` method.

        Returns
        -------
        None
        """
        json.dump(
            data,
            fp,
            ensure_ascii=self._ensure_ascii,
            indent=self._indent,
        )

    def _convert(self, obj: Any, attrs: list[AttrSpec] | None = None, objects: Sequence[Any] | None = None) -> JSONValue:
        """
        Convert any object to a JSON-compatible value.

        Parameters
        ----------
        obj: Any
            Primary object to convert.
        attrs: list[AttrSpec] | None
            Attribute specifications.
        objects: Sequence[Any] | None
            Additional objects for multi-object attribute access.

        Returns
        -------
        JSONValue
            A JSON-compatible value.
        """
        # Fast path: primitives (most common case)
        if isinstance(obj, self._PRIMITIVES):
            return obj

        # Enums
        if isinstance(obj, Enum):
            return self._convert_enum(obj)

        # Datetime types
        if isinstance(obj, self._DATETIME_TYPES):
            return self._convert_datetime(obj)

        # Timedelta
        if isinstance(obj, datetime.timedelta):
            return self._convert_timedelta(obj)

        # Bytes
        if isinstance(obj, self._BYTES_TYPES):
            return self._convert_bytes(obj)

        if isinstance(obj, Mapping):
            return self._convert_mapping(obj)

        # Iterables (list, tuple, set, etc.)
        if isinstance(obj, Iterable):
            return self._convert_iterable(obj)

        # Specific attributes requested
        if attrs is not None:
            return self._convert_with_attrs(obj, attrs, objects)

        # Dataclasses
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            return self._convert_dataclass(obj)

        # Slotted objects
        slots = self._get_slots_cached(type(obj))
        if slots:
            return self._convert_slotted(obj, slots)

        # Objects with __dict__
        if hasattr(obj, "__dict__"):
            return self._convert_dict_obj(obj)

        # Fallback: string representation
        return str(obj)

    def _convert_mapping(self, obj: Mapping[Any, Any]) -> dict[str, Any]:
        """
        Convert mapping to dict with recursive conversion.

        Parameters
        ----------
        obj: Mapping[Any, Any]
            Mapping to convert.

        Returns
        -------
        dict[str, Any]
            Converted dictionary.
        """
        result = {str(k): self._convert(v) for k, v in obj.items()}
        return self._filter_dict(result)

    def _convert_iterable(self, obj: Iterable[Any]) -> list[Any]:
        """
        Convert iterable to list with recursive conversion.

        Parameters
        ----------
        obj: Iterable[Any]
            Iterable to convert.

        Returns
        -------
        list[Any]
            Converted list.
        """
        # Use map for efficient conversion
        converted = map(self._convert, obj)
        if self._include_empty:
            return list(converted)
        # Use filterfalse with _is_empty for filtering
        return list(filterfalse(self._is_empty, converted))

    def _convert_with_attrs(self, obj: Any, attrs: list[AttrSpec], objects: Sequence[Any] | None = None) -> dict[str, Any]:
        """
        Convert object extracting only specified attributes.

        Parameters
        ----------
        obj: Any
            Object to convert.
        attrs: list[AttrSpec]
            Attribute specifications to extract.
        objects: Sequence[Any] | None
            Additional objects for multi-object attribute access.

        Returns
        -------
        dict[str, Any]
            Dictionary of extracted attributes.
        """
        result: dict[str, Any] = {}
        all_objects = [obj] if objects is None else list(objects)

        for label, indexed_paths in self._normalize_attrs(attrs):
            # Handle callable transformer
            if callable(indexed_paths):
                try:
                    value = self._convert(indexed_paths(obj))
                except Exception:
                    value = None
                if self._should_include(value):
                    result[label] = value
                continue

            # Handle fallback chain
            if isinstance(indexed_paths, FallbackChain):
                value = None
                for obj_idx, path in indexed_paths.paths:
                    target_obj = all_objects[obj_idx] if obj_idx < len(all_objects) else obj
                    try:
                        value = self._convert(self._resolve_attribute(target_obj, path))
                        if not self._is_empty(value):
                            break
                    except (AttributeError, KeyError):  # noqa: S112
                        continue
                if self._should_include(value):
                    result[label] = value
                continue

            if len(indexed_paths) == 1:
                obj_idx, path = indexed_paths[0]
                target_obj = all_objects[obj_idx] if obj_idx < len(all_objects) else obj
                value = self._convert(self._resolve_attribute(target_obj, path))
            else:
                # Multiple paths - create dict with last segment as key
                value = {}
                for obj_idx, path in indexed_paths:
                    target_obj = all_objects[obj_idx] if obj_idx < len(all_objects) else obj
                    key = self._get_attr_key(path)
                    value[key] = self._convert(self._resolve_attribute(target_obj, path))

            if self._should_include(value):
                result[label] = value

        return result

    def _convert_dataclass(self, obj: Any) -> dict[str, Any]:
        """
        Convert dataclass using `dataclasses.fields()` introspection.

        Parameters
        ----------
        obj: Any
            Dataclass instance.

        Returns
        -------
        dict[str, Any]
            Converted dictionary of public fields.
        """
        fields = dataclasses.fields(obj)
        result = {f.name: self._convert(getattr(obj, f.name)) for f in fields if not f.name.startswith("_")}
        return self._filter_dict(result)

    def _convert_slotted(self, obj: Any, slots: frozenset[str]) -> dict[str, Any]:
        """
        Convert object with __slots__.

        Parameters
        ----------
        obj: Any
            Slotted instance.
        slots: frozenset[str]
            The set of slot names.

        Returns
        -------
        dict[str, Any]
            Converted dictionary of public slots.
        """
        public_slots = (s for s in slots if not s.startswith("_"))
        result = {slot: self._convert(getattr(obj, slot)) for slot in public_slots if hasattr(obj, slot)}
        return self._filter_dict(result)

    def _convert_dict_obj(self, obj: Any) -> dict[str, Any]:
        """
        Convert object with __dict__.

        Parameters
        ----------
        obj: Any
            Object with `__dict__` attribute.

        Returns
        -------
        dict[str, Any]
            Converted dictionary of public attributes.
        """
        result = {k: self._convert(v) for k, v in vars(obj).items() if not k.startswith("_")}
        return self._filter_dict(result)

    def _filter_dict(self, d: dict[str, Any]) -> dict[str, Any]:
        """
        Filter dictionary based on include_empty setting.

        Parameters
        ----------
        d: dict[str, Any]
            Input dictionary.

        Returns
        -------
        dict[str, Any]
            Filtered dictionary.
        """
        if self._include_empty:
            return d
        return {k: v for k, v in d.items() if self._should_include(v)}


def to_json(
    *,
    path: Path,
    objects: Sequence[object],
    names: tuple[str | None, list[AttrSpec]] | None = None,
    indent: int = 4,
    include_empty: bool = True,
    ensure_ascii: bool = False,
) -> None:
    """
    Export objects to a JSON file using JSONExporter.

    Parameters
    ----------
    path: Path
        Output file path.
    objects: Sequence[object]
        Objects to serialize.
    names: tuple[str | None, list[AttrSpec]] | None
        Tuple of (root_key, attrs) for custom output structure. If `root_key`
        is None and `attrs` is provided, a best-effort key is inferred.
    indent: int
        Indentation for pretty-printing JSON. Default is 4.
    include_empty: bool
        Whether to include empty values. Default is True.
    ensure_ascii: bool
        Whether to escape non-ASCII characters. Default is False.

    Returns
    -------
    None
        Writes the JSON to `path`.
    """
    exporter = JSONExporter(
        include_empty=include_empty,
        indent=indent,
        ensure_ascii=ensure_ascii,
    )

    if names is not None:
        root_key, attrs = names
        if root_key is None and attrs:
            last = attrs[-1]
            if isinstance(last, tuple):
                root_key = last[0]
            elif isinstance(last, str):
                root_key = last
            else:
                root_key = "value"
        exporter.export(path, objects, root_key=root_key, attrs=attrs)
    else:
        exporter.export(path, objects)
