from typing import TypedDict, NotRequired, Required


# Base type for coordinates
class AdresCoordinaten(TypedDict):
    lat: float
    lon: float


# Base type for country/land
class AdresLand(TypedDict):
    code: str
    id: str
    naam: str
    name: str | None  # education search organization


# Base address type with common fields
class BaseAdres(TypedDict):
    huisnummer: str
    plaats: str
    postcode: str


# VestigingsAdres extends BaseAdres, adds extra and land
class VestigingsAdres(BaseAdres, total=False):
    extra: NotRequired[str | None]
    land: Required[AdresLand]


# OrganizationVestigingsAdres extends VestigingsAdres, adds coordinaten and locatiePlaats
class OrganizationVestigingsAdres(VestigingsAdres, total=False):
    coordinaten: NotRequired[AdresCoordinaten | None]
    locatiePlaats: NotRequired[str | None]
    straat: str  # make straat required for this type


# StudyLocationVestigingsAdres is a simple alias for BaseAdres with all required
class StudyLocationVestigingsAdres(BaseAdres):
    straat: str


# EducationDetailAdres extends BaseAdres, adds locatiePlaats and coordinaten
class EducationDetailAdres(BaseAdres, total=False):
    straat: Required[str]
    locatiePlaats: NotRequired[str | None]
    coordinaten: NotRequired[AdresCoordinaten | None]


EducatieSearchResultItemAdres = OrganizationVestigingsAdres
