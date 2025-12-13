"""Model voor studielocaties (scholen/vestigingen)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .adres import Adres

if TYPE_CHECKING:
    from internals._types.study_location import StudyLocationResult as StudyLocationResultPayload


__all__ = ("StudyLocation",)


class StudyLocation:
    """Representatie van een studielocatie uit de Stagemarkt API.

    Attributes
    ----------
    emailadres: str
        E-mailadres van de studielocatie.
    location_naam: str
        Naam van de studielocatie.
    logo_url: str | None
        URL naar het logo van de studielocatie, indien aanwezig.
    school_naam: str
        Naam van de school waartoe de studielocatie behoort.
    telefoonnummer: str
        Telefoonnummer van de studielocatie.
    vestigingsadres: Adres | None
        Vestigingsadres van de studielocatie, indien aanwezig.
    website: str
        Website van de studielocatie.
    """

    __slots__ = (
        "emailadres",
        "location_naam",
        "logo_url",
        "school_naam",
        "telefoonnummer",
        "vestigingsadres",
        "website",
    )

    def __init__(self, data: StudyLocationResultPayload) -> None:
        self.location_naam: str = data.get("locationName", "")
        self.school_naam: str = data.get("schoolName", "")
        self.emailadres: str = data.get("emailadres", "")
        self.telefoonnummer: str = data.get("telefoonnummer", "")
        self.website: str = data.get("website", "")
        self.logo_url: str = data.get("logoUrl", "")

        adres_data = data.get("vestigingsadres")
        self.vestigingsadres: Adres | None = Adres.from_dict(adres_data) if adres_data else None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} school_naam={self.school_naam!r} location_naam={self.location_naam!r}>"
