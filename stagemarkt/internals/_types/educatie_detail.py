from __future__ import annotations

from typing import TypedDict

from .adres import EducationDetailAdres
from .base import EducatieSearchResultItemLeerweg
from .kwalificatie import Kwalificatie
from .organisatie import EducationDetailOrganisatie
from .vergoedingen import EducatieSearchResultItemVergoeding


class EducationDetailKerntaakSubtaak(TypedDict):
    code: str
    naam: str
    uitvoerbaar: bool


class EducationDetailKerntaak(TypedDict):
    code: str
    naam: str
    subtaken: list[EducationDetailKerntaakSubtaak]


class EducationDetail(TypedDict):
    aantal: int
    contactpersoon: str
    emailadres: str
    telefoon: str
    id: str
    omschrijving: str
    titel: str
    wervendeTitel: str
    vaardigheden: str
    aanbieden: str
    website: str
    adres: EducationDetailAdres
    organisatie: EducationDetailOrganisatie
    kerntaken: list[EducationDetailKerntaak]
    kenmerken: list[str]
    media: list[str]
    vergoedingen: list[EducatieSearchResultItemVergoeding]
    bedragVan: int
    bedragTot: int
    kwalificatie: Kwalificatie
    startdatum: str | None
    einddatum: str | None
    leerweg: EducatieSearchResultItemLeerweg
    studyDescription: str | None
    gewijzigdDatum: str | None
    dagenPerWeek: str | int | None
