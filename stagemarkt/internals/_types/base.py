from typing import Literal, TypedDict

LocatieSuggestieBodyDataItemType = Literal["Plaats", "Regio", "Postcode"]
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
    "sbi",  # soort bedrijven
    "leerwegen",
    "bedrijfsgrootte",
    "landen",
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
    niveau: int
    term: str  # crebo
    pageSize: int


class LocatieSuggestieBodyParams(TypedDict, total=False):
    siteId: str
    term: str  # plaats, postcode, regio, etc
    lat: float
    lon: float


class EducatieSearchResultBodyParams(TypedDict, total=False):
    siteId: str
    pageSize: int
    page: int
    niveau: int
    type: int  # 1=stage, 2=leerbaan
    range: int
    crebocode: int
    plaatsPostcode: str
    buitenlandseBedrijven: bool
    sector: str  # see filters > id: sectoren.id
    companyType: str  # see filters -> id: sbi.id -- can be multiple times
    learningPath: str  # see filters -> id: leerwegen.id


class OrganizationSearchResultBodyParams(TypedDict, total=False):
    siteId: str
    pageSize: int
    page: int
    plaatsPostcode: str
    range: int
    crebocode: int
    organization: str
    companyType: str  # see filters -> id: sbi.id -- can be multiple times
    sort: str  # BPVO_REGISTRATIES # ???
    direction: Literal["ASCENDING", "DESCENDING"]
    aantalLeerplaatsen: int


class StudyLocationBodyParams(TypedDict, total=False):
    crebo: int
    lat: float
    lon: float


class BaseBodyParams(TypedDict, total=False):
    plaatsPostcode: str
    range: int
    crebocode: int
    niveau: int
