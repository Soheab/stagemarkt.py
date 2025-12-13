"""Detailmodellen voor organisaties.

Deze module bevat ``OrganisationDetail`` en submodellen die in de detailpayload
voorkomen, zoals erkenningen, kwalificaties en contactpersonen.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import datetime

from ..enums import Niveau
from .kerntaak import Kerntaak
from .organisatie import Organisatie

if TYPE_CHECKING:
    from ..internals._types.organisation_detail import (
        Equivalent as EquivalentPayload,
        Erkenning as ErkenningPayload,
        KwalificatieWithKerntaken as KwalificatieWithKerntakenPayload,
        OrganisationDetail as OrganisationDetailPayload,
        Person as PersonPayload,
    )


__all__ = (
    "OrganisationDetail",
    "OrganisationDetailEquivalent",
    "OrganisationDetailErkenning",
    "OrganisationDetailKwalificatie",
    "OrganisationDetailPerson",
)


class OrganisationDetailEquivalent:
    """Representatie van een equivalente kwalificatie in de organisatie.

    Attributes
    ----------
    crebocode: str
        CREBO-code van de equivalente kwalificatie.
    id: str
        Unieke ID van de equivalente kwalificatie.
    naam: str
        Naam van de equivalente kwalificatie.
    """

    __slots__ = ("crebocode", "id", "naam")

    def __init__(self, data: EquivalentPayload) -> None:
        self.crebocode: str = data.get("crebocode", "")
        self.id: str = data.get("id", "")
        self.naam: str = data.get("naam", "")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} crebocode={self.crebocode!r} naam={self.naam!r}>"


class OrganisationDetailKwalificatie:
    """Representatie van een kwalificatie van een organisatie.

    Attributes
    ----------
    crebocode: str
        CREBO-code van de kwalificatie.
    niveau: Niveau | None
        Niveau van de kwalificatie, indien aanwezig.
    kwalificatie: str
        Naam van de kwalificatie.
    sector: str | None
        Sector van de kwalificatie, indien aanwezig.
    sector_id: str | None
        Unieke sector-ID van de kwalificatie, indien aanwezig.
    """

    __slots__ = (
        "_einddatum",
        "_equivalenten",
        "_kerntaken",
        "_startdatum",
        "crebocode",
        "kwalificatie",
        "niveau",
        "sector",
        "sector_id",
    )

    def __init__(self, data: KwalificatieWithKerntakenPayload) -> None:
        self.crebocode: str = data.get("crebocode", "")
        self.kwalificatie: str = data.get("kwalificatie", "")
        self.niveau: Niveau | None = Niveau(niveau) if (niveau := data.get("niveau")) else None
        self.sector: str | None = data.get("sector")
        self.sector_id: str | None = data.get("sectorId")

        self._startdatum: str | None = data.get("startdatum")
        self._einddatum: str | None = data.get("einddatum")
        self._equivalenten = data.get("equivalenten", [])
        self._kerntaken = data.get("kerntaken", [])

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} crebocode={self.crebocode!r} kwalificatie={self.kwalificatie!r}>"

    @property
    def equivalenten(self) -> list[OrganisationDetailEquivalent]:
        """Lijst met equivalente kwalificaties."""

        return [OrganisationDetailEquivalent(e) for e in self._equivalenten]

    @property
    def kerntaken(self) -> list[Kerntaak]:
        """Kerntaken gekoppeld aan deze kwalificatie."""

        return [Kerntaak(k) for k in self._kerntaken]

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
    def eindigd_op(self) -> datetime.datetime | None:
        """:class:`datetime.datetime`: de einddatum van de leerplaats."""
        if self._startdatum:
            date_str = self._startdatum.rstrip("Z")
            try:
                return datetime.datetime.fromisoformat(date_str)
            except ValueError:
                return datetime.datetime.fromisoformat(date_str.split("T")[0])
        return None


class OrganisationDetailErkenning:
    """Representatie van een erkenning van een organisatie."""

    __slots__ = ("_einddatum", "_kwalificaties", "_startdatum")

    def __init__(self, data: ErkenningPayload) -> None:
        self._startdatum: str | None = data.get("startdatum")
        self._einddatum: str | None = data.get("einddatum")
        self._kwalificaties = data.get("kwalificaties", [])

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} start_op={self.start_op!r} eindigd_op={self.eindigd_op!r}>"

    @property
    def kwalificaties(self) -> list[OrganisationDetailKwalificatie]:
        """Kwalificaties binnen deze erkenning."""

        return [OrganisationDetailKwalificatie(k) for k in self._kwalificaties]

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
    def eindigd_op(self) -> datetime.datetime | None:
        """:class:`datetime.datetime`: de einddatum van de leerplaats."""
        if self._startdatum:
            date_str = self._startdatum.rstrip("Z")
            try:
                return datetime.datetime.fromisoformat(date_str)
            except ValueError:
                return datetime.datetime.fromisoformat(date_str.split("T")[0])
        return None


class OrganisationDetailPerson:
    """Representatie van een contactpersoon binnen een organisatie.

    Attributes
    ----------
    email: str | None
        De e-mailadres van de contactpersoon, indien aanwezig.
    voornaam: str | None
        De voornaam van de contactpersoon, indien aanwezig.
    achternaam: str | None
        De achternaam van de contactpersoon, indien aanwezig.
    initialen: str | None
        De initialen van de contactpersoon, indien aanwezig.
    voorvoegsel: str | None
        De voorvoegsel van de contactpersoon, indien aanwezig.
    mobiel: str | None
        Het mobiele telefoonnummer van de contactpersoon, indien aanwezig.
    telefoonnummer: str | None
        Het telefoonnummer van de contactpersoon, indien aanwezig.
    """

    __slots__ = ("achternaam", "email", "initialen", "mobiel", "telefoonnummer", "voornaam", "voorvoegsel")

    def __init__(self, data: PersonPayload) -> None:
        self.email: str | None = data.get("email")
        self.voornaam: str | None = data.get("firstName")
        self.achternaam: str | None = data.get("lastName")
        self.initialen: str | None = data.get("initials")
        self.voorvoegsel: str | None = data.get("insertion")
        self.mobiel: str | None = data.get("mobile")
        self.telefoonnummer: str | None = data.get("phone")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} voornaam={self.voornaam!r} achternaam={self.achternaam!r}>"


class OrganisationDetail(Organisatie):
    """Representatie van een stage/leerplaats uit de Stagemarkt API maar dan met meer details
    zoals telefoonnummer, contactpersonen, erkenningen, etc.

    Attributes
    ----------
    telefoonnummer: str | None
        Telefoonnummer van de organisatie.
    informatie_leren_werken: str | None
        Informatie over leren en werken bij de organisatie.
    informatie_student: str | None
        Informatie voor studenten bij de organisatie.
    personen: list[OrganisationDetailPerson]
        Lijst met contactpersonen van de organisatie.
    erkenning: OrganisationDetailErkenning | None
        Erkenninginformatie van de organisatie, indien aanwezig.
    """

    __slots__ = (
        "_erkenning",
        "_leerplaatsen",
        "_personen",
        "informatie_leren_werken",
        "informatie_student",
        "telefoonnummer",
    )

    def __init__(self, data: OrganisationDetailPayload) -> None:
        super().__init__(data)  # pyright: ignore[reportArgumentType]

        self.telefoonnummer: str | None = data.get("telefoonnummer")
        self.informatie_leren_werken: str | None = data.get("informatieLerenWerken")
        self.informatie_student: str | None = data.get("informatieStudent")

        self._personen = data.get("personen", [])
        self._leerplaatsen = data.get("leerplaatsen", [])
        self._erkenning = data.get("erkenning")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} naam={self.naam!r} id={self.id!r}>"

    @property
    def personen(self) -> list[OrganisationDetailPerson]:
        """list[:class:`OrganisationDetailPerson`]: lijst met contactpersonen van de organisatie."""
        return [OrganisationDetailPerson(p) for p in self._personen]

    @property
    def erkenning(self) -> OrganisationDetailErkenning | None:
        """OrganisationDetailErkenning | None: erkenninginformatie van de organisatie, indien aanwezig."""
        if self._erkenning:
            return OrganisationDetailErkenning(self._erkenning)
        return None
