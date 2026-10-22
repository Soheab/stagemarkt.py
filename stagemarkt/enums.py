from typing import Self
from enum import Enum

__all__ = (
    "Bedrijfsgrootte",
    "EducatieZoekType",
    "FileType",
    "FilterType",
    "FormulierSoort",
    "FormulierVeldType",
    "Kenmerk",
    "Land",
    "Leerweg",
    "LocatieType",
    "Niveau",
    "ProbleemSoort",
    "Regio",
    "Sector",
    "SoortBedrijf",
    "Sortering",
    "StartBinnen",
    "Straal",
    "VergoedingSoort",
)


class FileType(Enum):
    EXCEL = "xlsx"
    HTML = "html"
    JSON = "json"

    @classmethod
    def from_extension(cls, ext: str) -> Self:
        return cls(ext.removeprefix("."))


class LocatieType(Enum):
    """Soort zoekgebied (``locatieType``)."""

    PLAATS = "Plaats"
    REGIO = "Regio"
    POSTCODE = "Postcode"
    LAND = "Land"


class Leerweg(Enum):
    BBL = "acf992a3-efee-4537-9275-9e6b1b7a8fe3"
    BOL = "2468c1a0-ad7b-4209-b27b-b12ae0e3d1d2"


class EducatieZoekType(Enum):
    STAGE = 1
    LEERBAAN = 2


class Sortering(Enum):
    """Sorteeropties (``sort``) voor educaties en organisaties.

    De website toont voor leerbedrijven alleen ``RELEVANTIE``, ``NAAM_A_Z``,
    ``NAAM_Z_A`` en ``ACTUALITEIT``; de overige waarden worden wel door de API
    geaccepteerd.
    """

    RELEVANTIE = "RELEVANTIE"
    ACTUALITEIT = "ACTUALITEIT"
    AFSTAND = "AFSTAND"
    SALARIS = "SALARIS"
    BAANKANS = "BAANKANS"
    STARTDATUM = "STARTDATUM"
    NAAM_A_Z = "ALFABETISCHE_VOLGORDE_ORGANISATIENAAM"
    NAAM_Z_A = "OMGEKEERDE_ALFABETISCHE_VOLGORDE_ORGANISATIENAAM"
    BEDRIJFSGROOTTE = "BEDRIJFSGROOTTE"
    BPVO_REGISTRATIES = "BPVO_REGISTRATIES"
    AANTAL_LEERBANEN = "AANTAL_LEERBANEN"


class Bedrijfsgrootte(Enum):
    ZZP = "78cf9c53-cc8f-e311-9fd3-0050568a3da5"
    MEDEWERKERS_2_9 = "dabaaa7a-bf0b-437d-ae64-fb25c9f604ce"
    MEDEWERKERS_10_50 = "764d9e2d-8398-4cc3-a131-3cebe0f67876"
    MEDEWERKERS_51_100 = "dc43f5fe-27d8-df11-ae3c-001372415b01"
    MEDEWERKERS_101_250 = "7d0de40c-28d8-df11-ae3c-001372415b01"
    MEDEWERKERS_251_500 = "8420e71e-28d8-df11-ae3c-001372415b01"
    MEDEWERKERS_500_PLUS = "be389940-28d8-df11-ae3c-001372415b01"


class VergoedingSoort(Enum):
    REISKOSTENVERGOEDING = "a0c0cc96-7bd3-eb11-8235-00224882c087"
    ONKOSTENVERGOEDING = "ac16dd77-c530-f011-8c4e-7c1e52505ae1"
    STAGEVERGOEDING = "a4c0cc96-7bd3-eb11-8235-00224882c087"
    SALARIS = "763b3b59-ba30-f011-8c4e-7c1e52505ae1"


class Kenmerk(Enum):
    # Kenmerken van leerplaatsen (education-search)
    BEGELEIDING_OP_MAAT = "fb16c3ec-9641-e911-a965-000d3a38ad05"
    FYSIEKE_TOEGANKELIJKHEID = "467acfda-9641-e911-a965-000d3a38ad05"
    VASTE_BAAN = "6293559d-90fe-eb11-94ef-00224880e5e5"
    MBO_CERTIFICAAT = "d7abaf39-89fe-eb11-94ef-00224880e5e5"
    PRAKTIJKVERKLARING = "76b79697-89fe-eb11-94ef-00224880e5e5"
    # Kenmerken van leerbedrijven (organization-search)
    ZIJ_INSTROMERS = "f7f68a22-84fe-eb11-94ef-00224880e5e5"
    INTERNATIONALISATION_AT_HOME = "6c06a460-84fe-eb11-94ef-00224880e5e5"


class Sector(Enum):
    AFBOUW_HOUT_EN_ONDERHOUD = "e8bcd232-df4f-4259-8dc6-e327fe0ffb8e"
    AMBACHT_LABORATORIUM_GEZONDHEIDSTECHNIEK = "8a34cf88-ab19-4e70-8d4b-004c575c493a"
    BOUW_EN_INFRA = "4a82124d-d31f-44f9-a5d3-7348f6c439e5"
    ECONOMIE_EN_ADMINISTRATIE = "ea9c22f8-91de-4424-a355-2216afea8457"
    ENTREE = "d9807a87-e463-49e9-b7b3-06d1ec67dea4"
    HANDEL_MODE_ONDERNEMERSCHAP = "9f457708-62c1-4c1b-a39d-6bc778fd6b57"
    HORECA_EN_BAKKERIJ = "702d205f-66e3-4c49-8ea4-5219f7264ca8"
    ICT = "87c539b1-192b-4418-be0e-01e2df29bee7"
    MEDIA_EN_VORMGEVING = "35b7c213-be7a-4540-8a02-fa9c32d0460e"
    MOBILITEIT_EN_VOERTUIGEN = "ab18ea59-3852-4742-89fb-5b11510ac2ff"
    SPORT = "c86f3e64-164e-4743-93e0-e80184678c3a"
    TECHNIEK_EN_PROCESINDUSTRIE = "9fb032a7-96e5-4383-adac-a9a435b56ef7"
    TOERISME_EN_RECREATIE = "9eb0fc90-fc85-420e-b767-6ce16b8ab58b"
    TRANSPORT_SCHEEPVAART_LOGISTIEK = "9f4d5391-87d2-48ea-bbe4-035fb2215da5"
    UITERLIJKE_VERZORGING = "e9286ccc-71ba-4fe9-ab55-34c7fe66a876"
    VEILIGHEID = "0155dac2-88db-4cf3-89e7-fc89c269fab1"
    VMBO_PRO_VSO = "bc93e61d-646c-4ab7-bc76-c88dc70d6224"
    VOEDSEL_NATUUR_LEEFOMGEVING = "b195a344-48eb-4a51-b6d4-fb082650f9c2"
    ZORG_EN_WELZIJN = "0dd6dc35-bcc9-4042-b80b-7b091dae99bc"


class SoortBedrijf(Enum):
    """Een selectie van bedrijfstypen (SBI).

    Er bestaan er veel meer; gebruik ``StagemarktClient.haal_filter_opties`` om
    alle beschikbare waarden voor een zoekopdracht op te halen.
    """

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
    FINANCIELE_HOLDINGS = "43ab4f5e-b356-e011-87cd-001372415b01"
    OVERIGE_IT_DIENSTVERLENING = "31ab4f5e-b356-e011-87cd-001372415b01"
    OVERIGE_ZAKELIJKE_DIENSTVERLENING = "f8f44764-b356-e011-87cd-001372415b01"
    RECLAMEBUREAUS = "e9f44764-b356-e011-87cd-001372415b01"
    MARKT_EN_OPINIEONDERZOEK = "ecf44764-b356-e011-87cd-001372415b01"


class ProbleemSoort(Enum):
    """Soort probleem bij het melden van een fout in een stage ("Klopt iets niet?")."""

    STAGE_VERVULD = "stageVervuld"
    ONJUISTE_CONTACTGEGEVENS = "onjuisteContactgegevens"
    TEKSTFOUT = "tekstFout"
    ONDUIDELIJKE_BESCHRIJVING = "onduidelijkeBeschrijving"
    DISCRIMINERENDE_TEKST = "discriminerendeTekst"
    ANDERS = "anders"


class Niveau(Enum):
    """MBO niveau van 1 tot en met 4, of 0 voor pro, vso en vmbo."""

    PRO_VSO_VMBO = 0
    MBO_1 = 1
    MBO_2 = 2
    MBO_3 = 3
    MBO_4 = 4


class Straal(Enum):
    KM_5 = 5
    KM_10 = 10
    KM_15 = 15
    KM_25 = 25
    KM_50 = 50
    KM_75 = 75
    KM_100 = 100


class StartBinnen(Enum):
    """Startdatum-filter (``startInMonths``): leerplaatsen die binnen dit aantal maanden starten."""

    EEN_MAAND = 1
    DRIE_MAANDEN = 3
    ZES_MAANDEN = 6


class FormulierSoort(Enum):
    """ID's van de formulieren op stagemarkt.nl (uit het CMS; kunnen door SBB gewijzigd worden)."""

    SOLLICITATIE = "e2f49d2f-76b5-428c-ae44-a2b274573833"
    VRAAG_OVER_STAGE = "661a0c6c-6bc0-48fc-bbc8-91565a19d1e6"
    VRAAG_AAN_LEERBEDRIJF = "074a37d5-7ab3-488a-8ea6-6b421f45e5f2"
    KLOPT_IETS_NIET = "f4e9aae4-c029-4c3c-b403-1b200e98c7da"
    MAIL_ALERT_AANMAKEN = "62028b5ce4304ca0a2bcc8555f77cc0d"
    MAIL_ALERT_WIJZIGEN = "63feada0949e4783be28016b4cc322fe"


class FormulierVeldType(Enum):
    """Soort veld in een formulier."""

    KORT_ANTWOORD = "Short answer"
    LANG_ANTWOORD = "Long answer"
    BESTAND = "File upload"
    TOESTEMMING = "Data Consent"
    CHECKBOX = "Checkbox"
    KEUZE = "Single choice"
    VERBORGEN = "Hidden"


class FilterType(Enum):
    """Soort zoekfilter zoals ingesteld in het CMS."""

    AUTOCOMPLETE = "dropdown-autocomplete"
    VAST = "dropdown-static"
    DYNAMISCH = "dropdown-dynamic"
    INVOER = "input"


class Regio(Enum):
    """Regio's (``regio``), zie ook ``StagemarktClient.haal_regios``."""

    ACHTERHOEK = "c5c506ce-03ca-e211-a270-001372415b01"
    AMERSFOORT = "dbc506ce-03ca-e211-a270-001372415b01"
    DRECHTSTEDEN = "c6c506ce-03ca-e211-a270-001372415b01"
    DRENTHE = "c7c506ce-03ca-e211-a270-001372415b01"
    FLEVOLAND = "c8c506ce-03ca-e211-a270-001372415b01"
    FOOD_VALLEY = "c9c506ce-03ca-e211-a270-001372415b01"
    FRIESLAND = "cac506ce-03ca-e211-a270-001372415b01"
    GOOI_EN_VECHTSTREEK = "cbc506ce-03ca-e211-a270-001372415b01"
    GORINCHEM = "ccc506ce-03ca-e211-a270-001372415b01"
    GRONINGEN = "cdc506ce-03ca-e211-a270-001372415b01"
    GROOT_AMSTERDAM = "cec506ce-03ca-e211-a270-001372415b01"
    HAAGLANDEN = "cfc506ce-03ca-e211-a270-001372415b01"
    HELMOND_DE_PEEL = "d0c506ce-03ca-e211-a270-001372415b01"
    HOLLAND_RIJNLAND = "d1c506ce-03ca-e211-a270-001372415b01"
    MIDDEN_BRABANT = "d3c506ce-03ca-e211-a270-001372415b01"
    MIDDEN_GELDERLAND = "d4c506ce-03ca-e211-a270-001372415b01"
    MIDDEN_HOLLAND = "d5c506ce-03ca-e211-a270-001372415b01"
    MIDDEN_LIMBURG = "d6c506ce-03ca-e211-a270-001372415b01"
    MIDDEN_UTRECHT = "d7c506ce-03ca-e211-a270-001372415b01"
    NOORD_HOLLAND_NOORD = "d8c506ce-03ca-e211-a270-001372415b01"
    NOORD_LIMBURG = "d9c506ce-03ca-e211-a270-001372415b01"
    NOORDOOST_BRABANT = "dac506ce-03ca-e211-a270-001372415b01"
    REGIO_ZWOLLE = "d2c506ce-03ca-e211-a270-001372415b01"
    RIJK_VAN_NIJMEGEN = "e3c506ce-03ca-e211-a270-001372415b01"
    RIJNMOND = "dcc506ce-03ca-e211-a270-001372415b01"
    RIVIERENLAND = "ddc506ce-03ca-e211-a270-001372415b01"
    STEDENDRIEHOEK_EN_NOORDWEST_VELUWE = "dec506ce-03ca-e211-a270-001372415b01"
    TWENTE = "dfc506ce-03ca-e211-a270-001372415b01"
    WEST_BRABANT = "e0c506ce-03ca-e211-a270-001372415b01"
    ZAANSTREEK_WATERLAND = "e1c506ce-03ca-e211-a270-001372415b01"
    ZEELAND = "e2c506ce-03ca-e211-a270-001372415b01"
    ZUID_HOLLAND_CENTRAAL = "e4c506ce-03ca-e211-a270-001372415b01"
    ZUID_KENNEMERLAND_EN_IJMOND = "e5c506ce-03ca-e211-a270-001372415b01"
    ZUID_LIMBURG = "e6c506ce-03ca-e211-a270-001372415b01"
    ZUIDOOST_BRABANT = "e7c506ce-03ca-e211-a270-001372415b01"


class Land(Enum):
    """Landen (``land``) met ISO-landcode als waarde.

    Dit zijn de landen waar op het moment van schrijven erkende leerbedrijven zitten.
    """

    ALBANIE = "AL"
    ALGERIJE = "DZ"
    ANGOLA = "AO"
    ANGUILLA = "AI"
    ANTIGUA_EN_BARBUDA = "AG"
    ARGENTINIE = "AR"
    ARUBA = "AW"
    AUSTRALIE = "AU"
    AZERBEIDZJAN = "AZ"
    BANGLADESH = "BD"
    BELGIE = "BE"
    BOLIVIA = "BO"
    BONAIRE_SINT_EUSTATIUS_EN_SABA = "BQ"
    BOSNIE_EN_HERZEGOVINA = "BA"
    BOTSWANA = "BW"
    BRAZILIE = "BR"
    BULGARIJE = "BG"
    CANADA = "CA"
    CHILI = "CL"
    CHINA = "CN"
    COLOMBIA = "CO"
    COSTA_RICA = "CR"
    CURACAO = "CW"
    CYPRUS = "CY"
    DENEMARKEN = "DK"
    DOMINICAANSE_REPUBLIEK = "DO"
    DUITSLAND = "DE"
    ECUADOR = "EC"
    EGYPTE = "EG"
    ESTLAND = "EE"
    FAROER = "FO"
    FILIPIJNEN = "PH"
    FINLAND = "FI"
    FRANKRIJK = "FR"
    GAMBIA = "GM"
    GEORGIE = "GE"
    GHANA = "GH"
    GRIEKENLAND = "GR"
    GUADELOUPE = "GP"
    GUATEMALA = "GT"
    HONGARIJE = "HU"
    HONGKONG = "HK"
    IERLAND = "IE"
    IJSLAND = "IS"
    INDIA = "IN"
    INDONESIE = "ID"
    ITALIE = "IT"
    JAPAN = "JP"
    JORDANIE = "JO"
    KAAPVERDIE = "CV"
    KENIA = "KE"
    KOSOVO = "KO"
    KROATIE = "HR"
    LAOS = "LA"
    LETLAND = "LV"
    LITOUWEN = "LT"
    LUXEMBURG = "LU"
    MACEDONIE = "MK"
    MADAGASKAR = "MG"
    MALAWI = "MW"
    MALDIVEN = "MV"
    MALEISIE = "MY"
    MALTA = "MT"
    MAROKKO = "MA"
    MAURITIUS = "MU"
    MEXICO = "MX"
    MONACO = "MC"
    MONGOLIE = "MN"
    MONTENEGRO = "ME"
    NAMIBIE = "NA"
    NEDERLAND = "NL"
    NEPAL = "NP"
    NIEUW_ZEELAND = "NZ"
    NOORWEGEN = "NO"
    OEGANDA = "UG"
    OOSTENRIJK = "AT"
    PANAMA = "PA"
    PARAGUAY = "PY"
    PERU = "PE"
    POLEN = "PL"
    PORTUGAL = "PT"
    ROEMENIE = "RO"
    RWANDA = "RW"
    SAINT_LUCIA = "LC"
    SENEGAL = "SN"
    SERVIE = "RS"
    SINGAPORE = "SG"
    SINT_MAARTEN_FR = "MF"
    SINT_MAARTEN_NL = "SX"
    SLOVENIE = "SI"
    SLOWAKIJE = "SK"
    SPANJE = "ES"
    SRI_LANKA = "LK"
    SURINAME = "SR"
    TAIWAN = "TW"
    TANZANIA = "TZ"
    THAILAND = "TH"
    TSJECHIE = "CZ"
    TUNESIE = "TN"
    TURKIJE = "TR"
    VERENIGDE_ARABISCHE_EMIRATEN = "AE"
    VERENIGDE_STATEN = "US"
    VERENIGD_KONINKRIJK = "GB"
    VIETNAM = "VN"
    ZAMBIA = "ZM"
    ZIMBABWE = "ZW"
    ZUID_AFRIKA = "ZA"
    ZUID_KOREA = "KR"
    ZWEDEN = "SE"
    ZWITSERLAND = "CH"
