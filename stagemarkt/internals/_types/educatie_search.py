from __future__ import annotations

from typing import TypedDict

from .adres import EducatieSearchResultItemAdres
from .organisatie import EducatieSearchResultItemOrganisatie
from .base import EducatieSearchResultItemLeerweg
from .vergoedingen import EducatieSearchResultItemVergoeding
from .afbeelding import Afbeelding
from .kwalificatie import Kwalificatie
from .filters import Filter


class EducatieSearchResult(TypedDict):
    totalCount: int
    totalPages: int
    pageNumber: int
    filters: list[Filter]
    items: list[EducatieSearchResultItem]


class EducatieSearchResultItem(TypedDict):
    titel: str
    wervendeTitel: str
    leerplaatsId: str
    afstand: float | None
    vergoedingen: list[EducatieSearchResultItemVergoeding]
    bedragVan: int
    bedragTot: int
    adres: EducatieSearchResultItemAdres
    leerweg: EducatieSearchResultItemLeerweg
    startdatum: str | None  # ISO
    kenmerken: list[str]
    kwalificatie: Kwalificatie
    organisatie: EducatieSearchResultItemOrganisatie
    afbeeldingen: list[Afbeelding]
    gewijzigdDatum: str | None  # ISO
    dagenPerWeek: int | None


class EducatieSearchResultItemKwalificatie(TypedDict):
    niveaunaam: str
    crebocode: str
