"""Modellen voor opleiding-suggesties."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from internals._types.opleiding_suggestions import (
        OpleidingSuggestie as OpleidingSuggestiePayload,
        OpleidingSuggestieBodyDataItem as OpleidingSuggestieBodyDataItemPayload,
    )


__all__ = ("Opleiding", "OpleidingSuggestie")


class Opleiding:
    """Opleiding-item uit een suggestieresultaat.

    Attributes
    ----------
    crebo_code: int | None
        CREBO-code van de opleiding, indien aanwezig.
    equivalenten: list[str]
        Lijst met equivalenten van de opleiding.
    label: str | None
        Label van de opleiding, indien aanwezig.
    synoniemen: list[str]
        Lijst met synoniemen van de opleiding.
    value: str | None
        Waarde van de opleiding, indien aanwezig. Meestal "label (creboCode)".
    """

    __slots__ = ("crebo_code", "equivalenten", "label", "synoniemen", "value")

    def __init__(self, data: OpleidingSuggestieBodyDataItemPayload) -> None:
        self.crebo_code: int | None = data.get("creboCode")
        self.equivalenten: list[str] = data.get("equivalenten", [])
        self.label: str | None = data.get("label")
        self.synoniemen: list[str] = data.get("synoniemen", [])
        self.value: str | None = data.get("value")  # label (creboCode)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} label={self.label!r} crebo_code={self.crebo_code}>"


class OpleidingSuggestie:
    """Representatie van een opleiding-suggestie resultaat van de Stagemarkt API.

    Zie :attr:`.opleidingen` voor de lijst met opleiding-suggesties.
    """

    __slots__ = (
        "_opleidingen",
        "has_next_page",
        "has_previous_page",
        "page_number",
        "total_count",
        "total_pages",
    )

    def __init__(self, data: OpleidingSuggestiePayload) -> None:
        body_data = data.get("body", {}).get("data", {})

        self.has_next_page: bool = body_data.get("hasNextPage", False)
        self.has_previous_page: bool = body_data.get("hasPreviousPage", False)
        self.page_number: int = body_data.get("pageNumber", 0)
        self.total_count: int = body_data.get("totalCount", 0)
        self.total_pages: int = body_data.get("totalPages", 0)

        items = body_data.get("items", [])
        self._opleidingen = [Opleiding(item) for item in items]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} total_count={self.total_count} page_number={self.page_number}>"

    @property
    def opleidingen(self) -> list[Opleiding]:
        """list[:class:`Opleiding`]: lijst met opleiding-suggesties."""
        return self._opleidingen
