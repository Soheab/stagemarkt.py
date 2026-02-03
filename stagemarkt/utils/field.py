from typing import Any, Self
from collections.abc import Callable
from operator import attrgetter, itemgetter

from .misc import NoValue

__all__ = ("Field", "FieldOption")


def is_empty(value: object) -> bool:
    if value is None or value is False or value is NoValue:
        return True
    if isinstance(value, (str, list, dict, tuple, set, frozenset)):
        return len(value) == 0
    return bool(isinstance(value, (int, float)) and value == 0)


def build_getter(
    *,
    path: str,
    index: int | None = None,
    fallback: "FieldOption | None" = None,
) -> Callable[[object], object]:
    def primary(obj: object) -> object:
        try:
            if index is None:
                return attrgetter(path)(obj)
            return itemgetter(index)(attrgetter(path)(obj))
        except Exception:  # noqa: BLE001
            return None

    if not fallback:
        return primary

    def actual(obj: object) -> object:
        value = primary(obj)
        if value is not None:
            return value
        try:
            return fallback.get(obj)
        except Exception:  # noqa: BLE001
            return None

    return actual


class FieldOption:
    """
    Single attribute option inside a Field.

    Supports optional fallback, indexing, and per-option transforms.

    Examples
    --------
    Basic path:
        >>> FieldOption("organisatie.naam", label="Bedrijfsnaam")

    Index after attribute (e.g. `obj.items[0]`):
        >>> FieldOption("items", index=0, label="Eerste")

    Fallback chain:
        >>> FieldOption("email", fallback="contact.email")

    Transform the extracted value:
        >>> FieldOption("omschrijving").transform(lambda v: v[:100])
    """

    def __init__(
        self,
        path: str,
        *,
        label: str | None = NoValue,
        fallback: "str | FieldOption | None" = None,
        index: int | None = None,
        transform: Callable[[Any], Any] | None = None,
    ) -> None:
        self.path: str = path
        self.label: str | None = path.rsplit(".", maxsplit=1)[-1] if label is NoValue else label
        self.fallback: FieldOption | None = FieldOption(fallback) if isinstance(fallback, str) else fallback
        self.index: int | None = index
        self._transformer: Callable[[Any], Any] | None = transform

        self.__getter: Callable[[object], object] = build_getter(path=self.path, index=self.index, fallback=self.fallback)

    def transform(self, func: Callable[[Any], Any], /) -> Self:
        """
        Set a transformer for this option.

        The transformer receives the extracted value and returns a new value.
        """
        self._transformer = func
        return self

    def get(self, obj: object, *, include_empty: bool = True) -> Any:
        """
        Extract the option value from an object.

        Parameters
        ----------
        obj: object
            The object to extract from.
        include_empty: bool
            If False, empty values return None.
        """
        value = self.__getter(obj)
        if self._transformer is not None:
            value = self._transformer(value)
        if not include_empty and is_empty(value):
            return None
        return value


class Field:
    """
    Group of FieldOption entries that yields a dict with an optional label.

    The return shape is always a dict: `{label: value}` where `label` may be None.

    Examples
    --------
    Single field:
        >>> Field("organisatie.naam", label="Bedrijfsnaam")

    Multiple options (nested dict):
        >>> Field(label="Adres").add("adres.straat").add("adres.plaats")

    Fallback per option:
        >>> Field(label="Email").add("email", fallback="contact.email")

    Transform the whole field:
        >>> Field(label="Link").transform(lambda obj: f"https://example.com/{obj.id}")
    """

    def __init__(
        self,
        *options: str | FieldOption,
        label: str | None = None,
        transform: Callable[[Any], Any] | None = None,
    ) -> None:
        self.label: str | None = label
        self._transformer: Callable[[Any], Any] | None = transform
        self._getters: dict[str, FieldOption] = {}
        for value in options:
            self.__add_or_append(value)

    def _infer_label(self) -> str | None:
        paths = list(self._getters.keys())
        if not self._getters:
            return None
        if len(self._getters) == 1:
            option = next(iter(self._getters.values()))
            return option.label or option.path.rsplit(".", maxsplit=1)[-1]

        roots = {path.split(".", maxsplit=1)[0] for path in paths}
        if len(roots) == 1:
            return next(iter(roots))
        return paths[-1].rsplit(".", maxsplit=1)[-1]

    def export_label(self) -> str:
        """
        Label used for exports (always non-empty).

        Falls back to inferred label or "value".
        """
        return self.label or (self._infer_label() or "value")

    def header_label(self) -> str | None:
        """
        Label for header rows.

        Returns the explicit Field label if set; otherwise, the single option label
        (if exactly one option exists). Returns None when no header should be used.
        """
        if self.label is not None:
            return self.label
        if len(self._getters) == 1:
            option = next(iter(self._getters.values()))
            return option.label
        return None

    def add(
        self,
        path: str,
        *,
        label: str | None = NoValue,
        fallback: "str | FieldOption | None" = None,
        index: int | None = None,
    ) -> Self:
        """
        Add a new FieldOption by path.

        Parameters
        ----------
        path: str
            Attribute path to extract (e.g. "organisatie.email").
        label: str | None
            Optional label for this option.
        fallback: str | FieldOption | None
            Optional fallback path or FieldOption.
        index: int | None
            Optional index to apply after attribute access.
        """
        option = FieldOption(path, label=label, fallback=fallback, index=index)
        self._getters[option.path] = option
        return self

    def append(self, option: FieldOption, /) -> Self:
        """Append an existing FieldOption."""
        self._getters[option.path] = option
        return self

    def __add_or_append(self, option: FieldOption | str, /) -> Self:
        if isinstance(option, FieldOption):
            return self.append(option)
        return self.add(option)

    def get(self, obj: object, *, include_empty: bool = True) -> Any:
        """
        Extract values for this field from an object.

        Returns a dict in the form `{label: value}` where `label` may be None.
        """
        label = self.label

        if self._transformer is not None:
            value = self._transformer(obj)
            if not include_empty and is_empty(value):
                return {label: None}
            return {label: value}

        if not self._getters:
            return {label: {}}

        values: dict[str, object] = {}
        for option in self._getters.values():
            value = option.get(obj, include_empty=include_empty)
            if value is None and not include_empty:
                continue

            key = option.label or option.path.rsplit(".", maxsplit=1)[-1]
            values[key] = value

        if len(self._getters) == 1:
            return {label: next(iter(values.values()), None)}

        return {label: values}

    def transform(self, func: Callable[[Any], Any], /) -> Self:
        """Set a transformer for the entire field."""
        self._transformer = func
        return self
