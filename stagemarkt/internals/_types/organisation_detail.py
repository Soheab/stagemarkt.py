from __future__ import annotations

from typing import TypedDict


class AdresLand(TypedDict):
    code: str
    id: str
    name: str | None


class AdresCoordinaten(TypedDict):
    lat: float
    lon: float


class VestigingsAdres(TypedDict):
    extra: str | None
    huisnummer: str
    land: AdresLand
    plaats: str
    postcode: str
    regioId: str | None
    straat: str
    locatiePlaats: str | None
    coordinaten: AdresCoordinaten | None


class Person(TypedDict, total=False):
    email: str | None
    firstName: str | None
    initials: str | None
    insertion: str | None
    lastName: str | None
    mobile: str | None
    phone: str | None


class KerntaakSubtaak(TypedDict):
    id: str
    code: str
    naam: str
    uitvoerbaar: bool


class Kerntaak(TypedDict):
    aantalSubtaken: int
    aantalUitvoerbaar: int
    code: str
    id: str
    naam: str
    subtaken: list[KerntaakSubtaak]


class Equivalent(TypedDict):
    crebocode: str
    id: str
    naam: str


class KwalificatieWithKerntaken(TypedDict, total=False):
    einddatum: str | None
    startdatum: str | None
    crebocode: str
    kwalificatie: str
    niveau: int | None
    sector: str | None
    sectorId: str | None
    equivalenten: list[Equivalent]
    kerntaken: list[Kerntaak]


class Erkenning(TypedDict):
    einddatum: str | None  # iso
    startdatum: str | None  # iso
    kwalificaties: list[KwalificatieWithKerntaken]


class OrganisationDetail(TypedDict):
    aantalLeerplaatsen: int
    bedrijfsgrootte: str | None
    soortBedrijf: str | None
    emailadres: str | None
    leidenVaakOp: bool
    omschrijving: str | None
    id: str
    leerbedrijfId: str | None
    logoUrl: str | None
    naam: str
    kenmerken: list[str]
    telefoonnummer: str | None
    website: str | None
    personen: list[Person]
    vestigingsadres: VestigingsAdres
    leerplaatsen: list[dict]
    informatieLerenWerken: str | None
    informatieStudent: str | None
    erkenning: Erkenning | None
