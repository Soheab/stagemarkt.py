from __future__ import annotations

from typing import TYPE_CHECKING
import datetime

from ..enums import Leerweg
from .adres import Adres
from .afbeelding import Afbeelding
from .organisatie import Organisatie

if TYPE_CHECKING:
    from internals._types.educatie_detail import EducationDetail as EducationDetailPayload
    from internals._types.educatie_search import (
        EducatieSearchResultItem as EducatieSearchResultItemPayload,
        EducatieSearchResultItemKwalificatie as EducatieSearchResultItemKwalificatiePayload,
        EducatieSearchResultItemVergoeding as EducatieSearchResultItemVergoedingPayload,
    )


__all__ = ("Educatie", "Kwalificatie", "Vergoeding")


class Kwalificatie:
    """Representatie van een kwalificatie die bij een leerplaats hoort."""

    __slots__ = ("crebocode", "niveau_naam")

    def __init__(self, data: EducatieSearchResultItemKwalificatiePayload) -> None:
        self.niveau_naam: str = data.get("niveaunaam", "")
        self.crebocode: int = int(data.get("crebocode", 0))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} niveau_naam={self.niveau_naam!r} crebocode={self.crebocode}>"


class Vergoeding:
    """Representatie van een vergoeding die bij een leerplaats hoort."""

    __slots__ = ("id", "omschrijving")

    def __init__(self, data: EducatieSearchResultItemVergoedingPayload) -> None:
        self.id: str = data.get("id", "")
        self.omschrijving: str = data.get("omschrijving", "")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id!r} omschrijving={self.omschrijving!r}>"


class Educatie:
    """Representatie van een stage/leerplaats uit de Stagemarkt API.

    Attributes
    ----------
    title: str
        Titel van de leerplaats.
    wervende_title: str
        Wervende titel van de leerplaats.
    leerplaats_id: str
        Unieke ID van de leerplaats.
    afstand: float | None
        Afstand tot de opgegeven locatie in kilometers, indien beschikbaar.
    bedrag_van: int | None
        Minimale vergoeding voor de leerplaats, indien beschikbaar.
    bedrag_tot: int | None
        Maximale vergoeding voor de leerplaats, indien beschikbaar.
    leerweg: Leerweg
        Leerweg van de leerplaats.
    kenmerken: list[str]
        Lijst met kenmerken van de leerplaats.
    dagen_per_week: int | None
        Aantal dagen per week voor de leerplaats, indien beschikbaar.


    """

    __slots__ = (
        "_adres",
        "_afbeeldingen",
        "_gewijzigd_datum",
        "_kwalificatie",
        "_organisatie",
        "_startdatum",
        "_vergoedingen",
        "afstand",
        "bedrag_tot",
        "bedrag_van",
        "dagen_per_week",
        "kenmerken",
        "leerplaats_id",
        "leerweg",
        "title",
        "wervende_title",
    )

    def __init__(self, data: EducatieSearchResultItemPayload | EducationDetailPayload) -> None:
        self.title: str = data.get("titel", "")
        self.wervende_title: str = data.get("wervendeTitel", "")
        self.leerplaats_id: str = data.get("leerplaatsId") or data.get("id", "")
        self.afstand: float | None = data.get("afstand")
        self.bedrag_van: int = data.get("bedragVan")
        self.bedrag_tot: int = data.get("bedragTot")
        self.leerweg: Leerweg = Leerweg[data.get("leerweg", "BOL")]
        self.kenmerken: list[str] = data.get("kenmerken", [])

        try:
            dagen_per_week = int(data.get("dagenPerWeek", 0))  # pyright: ignore[reportArgumentType]
        except (TypeError, ValueError):
            dagen_per_week = 0

        self.dagen_per_week: int = dagen_per_week

        self._kwalificatie = data.get("kwalificatie")
        self._afbeeldingen = data.get("afbeeldingen", [])
        self._organisatie = data.get("organisatie")
        self._adres = data.get("adres")
        self._vergoedingen = data.get("vergoedingen", [])
        self._gewijzigd_datum = data.get("gewijzigdDatum")
        self._startdatum = data.get("startdatum")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} organisatie={self.organisatie!r}>"

    @property
    def gewijzigd_op(self) -> datetime.datetime | None:
        """:class:`datetime.datetime`: de datum/tijd waarop de leerplaats voor het laatst is gewijzigd."""

        if self._gewijzigd_datum:
            # Handle ISO 8601 format with optional milliseconds and 'Z'
            date_str = self._gewijzigd_datum.rstrip("Z")
            try:
                return datetime.datetime.fromisoformat(date_str)
            except ValueError:
                # Fallback: parse only the date part
                return datetime.datetime.fromisoformat(date_str.split("T")[0])
        return None

    @property
    def start_op(self) -> datetime.datetime | None:
        """:class:`datetime.datetime`: de startdatum van de leerplaats."""
        if self._startdatum:
            date_str = self._startdatum.rstrip("Z")
            try:
                return datetime.datetime.fromisoformat(date_str)
            except ValueError:
                return datetime.datetime.fromisoformat(date_str.split("T")[0])
        return None

    @property
    def adres(self) -> Adres | None:
        """:class:`Adres` | ``None``: het adres van de leerplaats."""
        if self._adres:
            return Adres.from_dict(self._adres)  # pyright: ignore[reportArgumentType]
        return None

    @property
    def vergoedingen(self) -> list[Vergoeding]:
        """list[:class:`Vergoeding`]: lijst met vergoedingen van de leerplaats."""

        return [Vergoeding(vdata) for vdata in self._vergoedingen]

    @property
    def organisatie(self) -> Organisatie | None:
        """:class:`Organisatie` | ``None``: de organisatie die de leerplaats aanbiedt."""
        if self._organisatie:
            return Organisatie(self._organisatie)  # pyright: ignore[reportArgumentType]
        return None

    @property
    def afbeeldingen(self) -> list[Afbeelding]:
        """list[:class:`Afbeelding`]: lijst met afbeeldingen die bij de leerplaats advertentie horen."""
        return [Afbeelding(adata) for adata in self._afbeeldingen]

    @property
    def kwalificatie(self) -> Kwalificatie | None:
        """:class:`Kwalificatie` | ``None``: de kwalificatie van de leerplaats."""
        if self._kwalificatie:
            return Kwalificatie(self._kwalificatie)  # pyright: ignore[reportArgumentType]
        return None
