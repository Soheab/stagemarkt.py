from typing import Literal, TypedDict

LocatieSuggestieBodyDataItemType = Literal["Plaats", "Regio", "Postcode", "Land"]
EducatieSearchResultItemLeerweg = Literal[
    "BOL",
    "BBL",
]
EducatieSearchResultItemLeerwegLabel = Literal[
    "BOL",
    "BBL",
]
EducatieSearchResultItemLeerwegLabelID = Literal[
    "2468c1a0-ad7b-4209-b27b-b12ae0e3d1d2",  # BOL
    "acf992a3-efee-4537-9275-9e6b1b7a8fe3",  # BBL
]
EducatieSearchResultFilterID = Literal[
    "kenmerken",
    "sectoren",
    "soortBedrijf",
    "leerweg",
    "bedrijfsgrootte",
    "land",
    "vergoedingen",
    "startInMonths",
    "alleWerkprocessenUitvoerbaar",
]
KnownVergoedingID = Literal[
    "a0c0cc96-7bd3-eb11-8235-00224882c087",  # Reiskostenvergoeding
    "ac16dd77-c530-f011-8c4e-7c1e52505ae1",  # Onkostenvergoeding
]
KnownVergoedingOmschrijving = Literal[
    "Reiskostenvergoeding",
    "Onkostenvergoeding",
]


class EducationDetailBodyParams(TypedDict):
    id: str
    siteId: str


class OpleidingSuggestieBodyParams(TypedDict, total=False):
    siteId: str
    opleidingsniveau: int
    term: str  # crebo
    pageSize: int


class LocatieSuggestieBodyParams(TypedDict, total=False):
    siteId: str
    term: str  # plaats, postcode, regio, etc
    lat: float
    lon: float


class SearchBodyParams(TypedDict, total=False):
    # Gedeelde parameters van education-search en organization-search
    siteId: str
    pageSize: int
    page: int
    opleidingsniveau: int
    straal: int  # zonder straal geeft een zoekopdracht met plaatsPostcode 0 resultaten
    crebocode: int
    plaatsPostcode: str
    locatieType: str  # Plaats, Postcode, Regio, Land
    sort: str  # zie enums.Sortering
    termen: str  # spatie-gescheiden trefwoorden
    soortBedrijf: str  # kan meerdere keren
    bedrijfsgrootte: str  # kan meerdere keren


class EducatieSearchResultBodyParams(SearchBodyParams, total=False):
    regio: str  # zie /regios
    leerweg: str  # maar één waarde, anders HTTP 500
    kenmerken: str  # kan meerdere keren (EN)
    vergoedingen: str  # kan meerdere keren
    startInMonths: int
    alleWerkprocessenUitvoerbaar: bool


class OrganizationSearchResultBodyParams(SearchBodyParams, total=False):
    organisatie: str  # (deel van) de naam
    sectoren: str
    kenmerken: str
    land: str  # landcode, bijv. NL
    buitenland: bool
    aantalLeerplaatsen: int  # alleen 0 is geldig: leerbedrijven zonder open leerplaatsen


class StudyLocationBodyParams(TypedDict, total=False):
    crebo: int
    lat: float
    lon: float
