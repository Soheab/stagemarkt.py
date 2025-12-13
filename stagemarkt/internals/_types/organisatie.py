from __future__ import annotations
from typing import TypedDict, NotRequired, Required

from .adres import (
    OrganizationVestigingsAdres,
    StudyLocationVestigingsAdres,
    EducationDetailAdres,
)
from .filters import Filter


class OrganisationSearchResult(TypedDict):
    items: list[OrganizationSearchResultItem]
    hasNextPage: bool
    hasPreviousPage: bool
    pageNumber: int
    totalCount: int
    totalPages: int
    filters: list[Filter]


class OrganisatieBase(TypedDict):
    id: Required[str]
    naam: Required[str]
    leerbedrijfId: Required[str]
    logoUrl: NotRequired[str | None]


class EducatieSearchResultItemOrganisatie(OrganisatieBase, total=False):
    # Only used in education search results
    vestigingsadres: StudyLocationVestigingsAdres


class OrganizationSearchResultItem(OrganisatieBase, total=False):
    # Used in organization search results
    aantalLeerplaatsen: int
    afstand: float | None
    bedrijfsgrootte: str | None
    email: str | None
    kenmerken: list[str]
    leidenVaakOp: bool
    vestigingsadres: OrganizationVestigingsAdres
    website: str | None


class EducationDetailOrganisatie(OrganisatieBase, total=False):
    # Used for detailed education organization info
    telefoonnummer: str
    emailadres: str
    website: str
    bedrijfsgrootte: str
    omschrijving: str | None
    vestigingsadres: EducationDetailAdres
