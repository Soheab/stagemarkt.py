from __future__ import annotations

from typing import TYPE_CHECKING, Any
import base64
from collections.abc import Iterable, Mapping, Sequence
import dataclasses
import datetime
from enum import Enum
import json
from pathlib import Path

from .base_exporter import BaseExporter, SortSpec

if TYPE_CHECKING:
    from _typeshed import SupportsWrite

    from .field import Field

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
        attrs: list[Field] | None = None,
        sort: SortSpec | None = None,
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
        attrs: list[Field] | None
            Attribute specifications to extract. If None, objects are
            converted using generic rules.

        Returns
        -------
        None
            Writes the JSON to `path`.
        """
        data = self._build_output(objects, root_key, attrs, sort)
        with path.open("w", encoding="utf-8") as f:
            self._dump(data, f)

    def dump(
        self,
        objects: Sequence[object],
        fp: SupportsWrite[str],
        *,
        root_key: str | None = None,
        attrs: list[Field] | None = None,
        sort: SortSpec | None = None,
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
        attrs: list[Field] | None
            Attribute specifications to extract.

        Returns
        -------
        None
            Writes JSON content to `fp`.
        """
        data = self._build_output(objects, root_key, attrs, sort)
        self._dump(data, fp)

    def dumps(
        self,
        objects: Sequence[object],
        *,
        root_key: str | None = None,
        attrs: list[Field] | None = None,
        sort: SortSpec | None = None,
    ) -> str:
        """
        Serialize objects to a JSON string.

        Parameters
        ----------
        objects: Sequence[object]
            Sequence of objects to serialize.
        root_key: str | None
            Optional root key to wrap the serialized list.
        attrs: list[Field] | None
            Attribute specifications to extract.

        Returns
        -------
        str
            The JSON string.
        """
        data = self._build_output(objects, root_key, attrs, sort)
        return json.dumps(
            data,
            ensure_ascii=self._ensure_ascii,
            indent=self._indent,
        )

    def serialize(self, obj: Any, attrs: list[Field] | None = None) -> JSONValue:
        """
        Serialize a single object to a JSON-compatible value.

        Parameters
        ----------
        obj: Any
            The object to serialize.
        attrs: list[Field] | None
            Attribute specifications to extract for `obj`.
        Returns
        -------
        JSONValue
            A JSON-compatible value (primitive, dict, or list).
        """
        return self._convert(obj, attrs)

    def _build_output(
        self,
        objects: Sequence[object],
        root_key: str | None,
        attrs: list[Field] | None,
        sort: SortSpec | None = None,
    ) -> JSONValue:
        """
        Build the final JSON structure.

        Parameters
        ----------
        objects: Sequence[object]
            Objects to serialize.
        root_key: str | None
            Optional root key to wrap the serialized list.
        attrs: list[Field] | None
            Attribute specifications to extract.

        Returns
        -------
        JSONValue
            Either a list of items or a dict with `root_key`.
        """
        items = [self._convert(obj, attrs) for obj in self._sort_objects(objects, sort)]
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

    def _convert(self, obj: Any, attrs: list[Field] | None = None) -> JSONValue:
        """
        Convert any object to a JSON-compatible value.

        Parameters
        ----------
        obj: Any
            Primary object to convert.
        attrs: list[Field] | None
            Attribute specifications.
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
            return obj.value

        # Datetime types
        if isinstance(obj, self._DATETIME_TYPES):
            return obj.isoformat()

        # Timedelta
        if isinstance(obj, datetime.timedelta):
            return obj.total_seconds()

        # Bytes
        if isinstance(obj, self._BYTES_TYPES):
            return self._bytes_to_text(obj)

        if isinstance(obj, Mapping):
            return self._convert_mapping(obj)

        # Iterables (list, tuple, set, etc.)
        if isinstance(obj, Iterable):
            return self._convert_iterable(obj)

        # Specific attributes requested
        if attrs is not None:
            return self._convert_with_attrs(obj, attrs)

        # Dataclasses
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            return self._convert_dataclass(obj)

        # Slotted objects
        slots = self._get_slots(type(obj))
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
        return {str(k): self._convert(v) for k, v in obj.items()}

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
        return list(converted)

    def _convert_with_attrs(self, obj: Any, attrs: list[Field]) -> dict[str, Any]:
        """
        Convert object extracting only specified attributes.

        Parameters
        ----------
        obj: Any
            Object to convert.
        attrs: list[Field]
            Attribute specifications to extract.
        Returns
        -------
        dict[str, Any]
            Dictionary of extracted attributes.
        """
        result: dict[str, Any] = {}
        for field in attrs:
            raw = field.get(obj, include_empty=self._include_empty)
            if not isinstance(raw, dict):
                continue
            for root, fields in raw.items():
                key = root if root is not None else field.export_label()
                if key is None:
                    continue
                value = self._convert(fields)
                if value is None and not self._include_empty:
                    continue
                result[key] = value
        return result

    def _bytes_to_text(self, obj: bytes | bytearray) -> str:
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
        return {f.name: self._convert(getattr(obj, f.name)) for f in fields if not f.name.startswith("_")}

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
        return {slot: self._convert(getattr(obj, slot)) for slot in public_slots if hasattr(obj, slot)}

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
        return {k: self._convert(v) for k, v in vars(obj).items() if not k.startswith("_")}


def to_json(
    *,
    path: Path,
    objects: Sequence[object],
    names: tuple[str | None, list[Field]] | None = None,
    indent: int = 4,
    include_empty: bool = True,
    ensure_ascii: bool = False,
    sort: SortSpec | None = None,
) -> None:
    """
    Export objects to a JSON file using JSONExporter.

    Parameters
    ----------
    path: Path
        Output file path.
    objects: Sequence[object]
        Objects to serialize.
    names: tuple[str | None, list[Field]] | None
        Tuple of (root_key, attrs) for custom output structure.
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
        exporter.export(path, objects, root_key=root_key, attrs=attrs, sort=sort)
    else:
        exporter.export(path, objects, sort=sort)
