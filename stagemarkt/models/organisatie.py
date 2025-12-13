"""Modellen voor organisaties/leerbedrijven."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .adres import Adres

if TYPE_CHECKING:
    from internals._types.organisatie import OrganizationSearchResultItem as OrganisationPayload


__all__ = ("Organisatie",)


class Organisatie:
    """Representatie van een organisatie/leerbedrijf uit de Stagemarkt API.

    Attributes
    ----------
    aantal_leerplaatsen: int
        Aantal leerplaatsen dat de organisatie aanbiedt.
    afstand: float | None
        Afstand tot de organisatie, indien aanwezig.
    bedrijfsgrootte: str | None
        Grootte van het bedrijf, indien aanwezig.
    email: str | None
        E-mailadres van de organisatie, indien aanwezig.
    id: str
        Unieke ID van de organisatie.
    kenmerken: list[str]
        Lijst met kenmerken van de organisatie.
    leerbedrijf_id: str
        Unieke leerbedrijf-ID van de organisatie.
    leiden_vaak_op: bool
        ``True`` als de organisatie vaak opleidt, anders ``False``.
    logo_url: str | None
        URL naar het logo van de organisatie, indien aanwezig.
    naam: str
        Naam van de organisatie.
    omschrijving: str | None
        Omschrijving van de organisatie, indien aanwezig.
    vestigingsadres: Adres | None
        Vestigingsadres van de organisatie, indien aanwezig.
    website: str | None
        Website van de organisatie, indien aanwezig.
    """

    __slots__ = (
        "aantal_leerplaatsen",
        "afstand",
        "bedrijfsgrootte",
        "email",
        "id",
        "kenmerken",
        "leerbedrijf_id",
        "leiden_vaak_op",
        "logo_url",
        "naam",
        "omschrijving",
        "vestigingsadres",
        "website",
    )

    def __init__(
        self,
        data: OrganisationPayload | dict[str, Any],
    ) -> None:
        # educatie search (EducatieSearchResultItemOrganisatiePayload)
        self.id: str = data.get("id", "")
        self.leerbedrijf_id: str = data.get("leerbedrijfId", "")
        self.naam: str = data.get("naam", "")
        self.logo_url: str | None = data.get("logoUrl")
        self.vestigingsadres: Adres | None = Adres.from_dict(adres) if (adres := data.get("vestigingsadres")) else None

        # organisatie search (OrganizationSearchResultItemPayload)
        self.aantal_leerplaatsen: int = data.get("aantalLeerplaatsen", 0)
        self.afstand: float | None = data.get("afstand")
        self.bedrijfsgrootte: str | None = data.get("bedrijfsgrootte")
        self.email: str | None = data.get("email") or data.get("emailadres")
        self.kenmerken: list[str] = data.get("kenmerken", [])
        self.leiden_vaak_op: bool = data.get("leidenVaakOp", False)
        self.website: str | None = data.get("website")

        # education detail search
        self.omschrijving: str | None = data.get("omschrijving")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} naam={self.naam!r} id={self.id!r}>"
