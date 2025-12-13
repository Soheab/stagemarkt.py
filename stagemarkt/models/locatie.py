"""Modellen voor locatie-suggesties."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..enums import LocatieType

if TYPE_CHECKING:
    from internals._types.location_suggestions import (
        LocatieSuggestie as LocatieSuggestiePayload,
        LocatieSuggestieBodyDataItem as LocatieSuggestieBodyDataItemPayload,
        LocatieSuggestieBodyDataItemPlaats as LocatieSuggestieBodyDataItemPlaatsPayload,
    )

__all__ = ("Locatie", "LocatiePlaats", "LocatieSuggestie")


class LocatiePlaats:
    """Representatie van een plaats binnen een locatie-suggestie uit de Stagemarkt API.

    Attributes
    ----------
    gemeente: str | None
        Gemeente van de plaats, indien aanwezig.
    lat: float | None
        Latitude van de plaats, indien aanwezig.
    lon: float | None
        Longitude van de plaats, indien aanwezig.
    naam: str | None
        Naam van de plaats, indien aanwezig.
    postcode: str | None
        Postcode van de plaats, indien aanwezig.
    provincie: str | None
        Provincie van de plaats, indien aanwezig.
    regio: str | None
        Regio van de plaats, indien aanwezig.
    """

    __slots__ = ("gemeente", "lat", "lon", "naam", "postcode", "provincie", "regio")

    def __init__(self, data: LocatieSuggestieBodyDataItemPlaatsPayload) -> None:
        self.gemeente: str | None = data.get("gemeente")
        self.regio: str | None = data.get("regio")
        self.lat: float | None = data.get("lat")
        self.lon: float | None = data.get("lon")
        self.naam: str | None = data.get("naam")
        self.postcode: str | None = data.get("postcode")
        self.provincie: str | None = data.get("provincie")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} naam={self.naam!r} gemeente={self.gemeente!r}>"


class Locatie:
    """Representatie van een locatie-suggestie uit de Stagemarkt API.

    Attributes
    ----------
    plaats: LocatiePlaats | None
        Plaatsinformatie van de locatie, indien aanwezig.
    suggestie: str | None
        De suggestietekst van de locatie, indien aanwezig.
    type: LocatieType | None
        Het type locatie, bijv. stad, provincie, etc., indien aanwezig.
    """

    __slots__ = ("plaats", "suggestie", "type")

    def __init__(self, data: LocatieSuggestieBodyDataItemPayload) -> None:
        self.suggestie: str | None = data.get("suggestie")
        self.type: LocatieType | None = LocatieType(ltype) if (ltype := data.get("type")) else None

        self.plaats: LocatiePlaats | None = LocatiePlaats(plaatsdata) if (plaatsdata := data.get("plaats")) else None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} suggestie={self.suggestie!r} type={self.type!r} plaats={self.plaats!r}>"


class LocatieSuggestie:
    """Locatie-suggestie resultaat van de Stagemarkt API.

    Zie :attr:`locaties` voor de lijst met locatie-suggesties.
    """

    __slots__ = ("_locaties",)

    def __init__(self, data: LocatieSuggestiePayload) -> None:
        body = data.get("body", {})
        items = body.get("data", {})

        self._locaties = [Locatie(item) for item in items]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} locaties={self.locaties!r}>"

    @property
    def locaties(self) -> list[Locatie]:
        """list[:class:`Locatie`]: lijst met locatie-suggesties."""
        return self._locaties
