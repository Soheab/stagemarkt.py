from typing import Self
from enum import Enum

__all__ = (
    "EducatieZoekType",
    "FileType",
    "Kenmerk",
    "Leerweg",
    "LocatieType",
    "Niveau",
    "Sector",
    "SoortBedrijf",
    "Straal",
)


class FileType(Enum):
    EXCEL = "xlsx"
    HTML = "html"
    JSON = "json"

    @classmethod
    def from_extension(cls, ext: str) -> Self:
        return cls(ext.removeprefix("."))


class LocatieType(Enum):
    PLAATS = "Plaats"
    REGIO = "Regio"
    POSTCODE = "Postcode"


class Leerweg(Enum):
    BBL = "acf992a3-efee-4537-9275-9e6b1b7a8fe3"
    BOL = "2468c1a0-ad7b-4209-b27b-b12ae0e3d1d2"


class EducatieZoekType(Enum):
    STAGE = 1
    LEERBAAN = 2


class Kenmerk(Enum):
    BEGELEIDING_OP_MAAT = "fb16c3ec-9641-e911-a965-000d3a38ad05"
    FYSIEKE_TOEGANKELIJKHEID = "467acfda-9641-e911-a965-000d3a38ad05"
    VASTE_BAAN = "6293559d-90fe-eb11-94ef-00224880e5e5"
    MBO_CERTIFICAAT = "d7abaf39-89fe-eb11-94ef-00224880e5e5"
    PRAKTIJKVERKLARING = "76b79697-89fe-eb11-94ef-00224880e5e5"


class Sector(Enum):
    ICT = "87c539b1-192b-4418-be0e-01e2df29bee7"
    ZORG_EN_WELZIJN = "0dd6dc35-bcc9-4042-b80b-7b091dae99bc"


class SoortBedrijf(Enum):
    GROOTHANDEL_COMPUTERS = "08aa4f5e-b356-e011-87cd-001372415b01"
    SOFTWARE_ONTWIKKELING = "2eab4f5e-b356-e011-87cd-001372415b01"
    GEGEVENSVERWERKING = "34ab4f5e-b356-e011-87cd-001372415b01"
    COMMUNICATIE_GRAFISCH_ONTWERP = "29c32618-98bb-e511-80cd-909e0336d287"
    DETAILHANDEL_KLEDING = "f96fed50-96bb-e511-80cd-909e0336d287"
    ORGANISATIEADVIESBUREAUS = "97ab4f5e-b356-e011-87cd-001372415b01"
    IT_ADVISERING = "2fab4f5e-b356-e011-87cd-001372415b01"
    LEASE_IMMATERIEEL = "14f54764-b356-e011-87cd-001372415b01"
    PARTICULIERE_BEVEILIGING = "27f54764-b356-e011-87cd-001372415b01"
    UITGEVERIJEN_TIJDSCHRIFTEN = "0fab4f5e-b356-e011-87cd-001372415b01"


class Niveau(Enum):
    """MBO niveau van 1 tot en met 4."""

    MBO_1 = 1
    MBO_2 = 2
    MBO_3 = 3
    MBO_4 = 4


class Straal(Enum):
    KM_5 = 5
    KM_10 = 10
    KM_15 = 15
    KM_25 = 25
    KM_100 = 100
