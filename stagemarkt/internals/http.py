from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Protocol,
    TypedDict,
)
import asyncio
import base64
from functools import partial
import json
import mimetypes
from pathlib import Path
import random

import aiohttp

from ..enums import (
    EducatieZoekType,
    FormulierSoort,
    Leerweg,
    LocatieType,
    Niveau,
    ProbleemSoort,
    Regio,
    Sortering,
    Straal,
)
from ..models import (
    Educatie,
    EducatieFilters,
    EducationDetail,
    FilterDefinitie,
    Formulier,
    LocatieSuggestie,
    MailAlert,
    MailAlertItem,
    OpleidingSuggestie,
    Organisatie,
    OrganisationDetail,
    RegioInfo,
    StagePreview,
    StudyLocation,
    ZoekFilter,
)

if TYPE_CHECKING:
    from _types.educatie_detail import EducationDetail as EducationDetailPayload
    from _types.educatie_search import (
        EducatieSearchResult as EducatieSearchResultPayload,
        EducatieSearchResultItem as EducatieSearchResultItemPayload,
    )
    from _types.formulier import (
        FilterDefinitie as FilterDefinitiePayload,
        Formulier as FormulierPayload,
        FormulierBestand as FormulierBestandPayload,
        MailAlert as MailAlertPayload,
        Vertalingen as VertalingenPayload,
    )
    from _types.opleiding_suggestions import (
        OpleidingSuggestie as OpleidingSuggestiePayload,
    )
    from _types.organisatie import (
        OrganisationSearchResult as OrganisationSearchResultPayload,
        OrganizationSearchResultItem as OrganizationSearchResultItemPayload,
    )
    from _types.organisation_detail import (
        OrganisationDetail as OrganisationDetailPayload,
    )
    from _types.regio import (
        OrganisatieSuggestie as OrganisatieSuggestiePayload,
        Regio as RegioPayload,
    )
    from _types.study_location import StudyLocationResult as StudyLocationResultPayload

if TYPE_CHECKING:
    from collections.abc import Coroutine

from typing import TypeVar

DataT = TypeVar("DataT", bound="MinimalData")

ItemT = TypeVar("ItemT")
DataT = TypeVar("DataT")  # No bound; accepts any response dict-like type


class MinimalCallable[T](Protocol):
    def __call__(self, *, page_size: int, page: int) -> Coroutine[Any, Any, T]: ...


class MinimalData(TypedDict, total=False):
    totalCount: int
    totalPages: int
    pageNumber: int
    items: list[Any]
    hasNextPage: bool
    hasPreviousPage: bool


class Paginator[ItemT, DataT]:
    def __init__(
        self,
        requester: MinimalCallable[Any],
        *,
        limit: int | None = None,
        max_page_size: int = 20,
        items_key: str = "items",
    ) -> None:
        self.current_page: int = 1
        self.has_more: bool = True
        self.limit: int | None = limit
        self.requester: MinimalCallable[Any] = requester
        self.items_key: str = items_key

        self.max_page_size: int = max_page_size

        self.__items: list[ItemT] = []

    async def collect(self) -> list[ItemT]:
        page_size = max(
            1,
            min(
                self.max_page_size,
                self.limit - len(self.__items) if self.limit is not None else self.max_page_size,
            ),
        )
        while self.has_more:
            response: dict[str, Any] = await self.requester(
                page_size=page_size,
                page=self.current_page,
            )
            items: list[ItemT] = response.get(self.items_key, [])
            self.__items.extend(items)

            if self.limit is not None and len(self.__items) >= self.limit:
                # Laatste pagina kan meer items bevatten dan nodig
                del self.__items[self.limit :]
                self.has_more = False
                break

            # Prefer hasNextPage if available, else fallback to page counting
            has_next = response.get("hasNextPage")
            if has_next is not None:
                self.has_more = bool(has_next)
            else:
                total_pages: int = response.get("totalPages", 1)
                self.has_more = self.current_page < total_pages

            if not self.has_more:
                break

            self.current_page += 1
            await asyncio.sleep(1)

        return self.__items


class HTTPClient:
    BASE_URL = "https://stagemarkt.nl/api/query-hub"
    EDUCATION_SEARCH_URL = f"{BASE_URL}/education-search"
    ORGANISATION_SEARCH_URL = f"{BASE_URL}/organization-search"
    LOCATIE_SUGGESTIES_URL = f"{BASE_URL}/locatie-suggesties"
    OPLEIDING_SUGGESTIES_URL = f"{BASE_URL}/opleiding-suggesties"
    ORGANISATIE_SUGGESTIES_URL = f"{BASE_URL}/organisatie-suggesties"
    REGIOS_URL = f"{BASE_URL}/regios"
    STUDY_LOCATIONS_URL = f"{BASE_URL}/study-locations"
    EDUCATION_DETAIL_URL = f"{BASE_URL}/education-detail"
    ORGANIZATION_DETAIL_URL = f"{BASE_URL}/organization-detail"

    SITE_URL = "https://stagemarkt.nl"
    UMBRACO_FILTERS_URL = f"{SITE_URL}/api/umbraco/filters"
    UMBRACO_CONTENT_URL = f"{SITE_URL}/api/umbraco/content"
    UMBRACO_FORM_URL = f"{SITE_URL}/api/umbraco/form"
    UMBRACO_TRANSLATIONS_URL = f"{SITE_URL}/api/umbraco/translations"
    FORMS_SUBMIT_URL = f"{SITE_URL}/api/forms/submit"
    MAIL_ALERTS_URL = f"{SITE_URL}/api/mail-alerts/mail-alerts"
    STAGE_PREVIEW_URL = f"{SITE_URL}/api/stages/preview"

    # Eerste teken van "umbracoFormSiteType" ("2 | stagemarkt") in de site-instellingen
    SITE_TYPE = "2"
    BESTAND_EXTENSIES = (".pdf", ".docx", ".doc", ".txt")
    MAX_BESTAND_GROOTTE = 5 * 1024 * 1024

    def __init__(self, session: aiohttp.ClientSession | None = None) -> None:
        self.__session: aiohttp.ClientSession | None = session

    def _generate_base_headers(self) -> dict[str, Any]:
        user_agents = [
            (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
            ),
            (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15"
            ),
        ]

        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "nl-NL,nl;q=0.9,en;q=0.8",
            "Referer": "https://stagemarkt.nl/",
            "Sec-CH-UA": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": random.choice(user_agents),
        }

    def get_base_params(
        self,
        *,
        niveau: Niveau | None = None,
        plaats_postcode: str | None = None,
        straal: Straal | int | None = None,
        crebocode: int | None = None,
        locatie_type: LocatieType | None = None,
        sortering: Sortering | None = None,
    ) -> dict[str, Any]:
        base: dict[str, Any] = {
            "siteId": "STAGEMARKT",
        }
        if niveau is not None:
            base["opleidingsniveau"] = niveau.value
        if plaats_postcode is not None:
            base["plaatsPostcode"] = plaats_postcode
        if straal is not None:
            base["straal"] = straal if isinstance(straal, int) else straal.value
        if crebocode is not None:
            base["crebocode"] = crebocode
        if locatie_type is not None:
            base["locatieType"] = locatie_type.value
        if sortering is not None:
            base["sort"] = sortering.value
        return base

    async def get_session(self) -> aiohttp.ClientSession:
        if self.__session is None or self.__session.closed:
            headers = self._generate_base_headers()
            self.__session = aiohttp.ClientSession(headers=headers)
        return self.__session

    async def close(self) -> None:
        if self.__session and not self.__session.closed:
            await self.__session.close()

        self.__session = None

    async def haal_locaties(
        self,
        *,
        term: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
    ) -> LocatieSuggestie:
        """Haal locatiesuggesties op voor een gegeven zoekterm of coördinaten.

        Parameters
        ----------
        term: str | None
            Zoekterm voor locaties (bijv. plaatsnaam, postcode of regio).
        lat: float | None
            Breedtegraad; samen met ``lon`` wordt de dichtstbijzijnde plaats gezocht.
        lon: float | None
            Lengtegraad; samen met ``lat`` wordt de dichtstbijzijnde plaats gezocht.

        Returns
        -------
        LocatieSuggestie
            Locatiesuggesties die overeenkomen met de zoekterm.
        """
        session = await self.get_session()
        params: dict[str, Any] = self.get_base_params()
        if term is not None:
            params["term"] = term
        if lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon

        async with session.get(self.LOCATIE_SUGGESTIES_URL, params=params) as resp:
            if resp.status == 500:
                # Soms geeft de API een 500 terug bij lege resultaten
                return LocatieSuggestie([])

            resp.raise_for_status()
            data = await resp.json()
            return LocatieSuggestie(data)

    async def __get_educations(
        self,
        *,
        page_size: int,
        page: int,
        params: list[tuple[str, Any]],
    ) -> EducatieSearchResultPayload:
        session = await self.get_session()
        # Maak een kopie om te voorkomen dat params hergebruikt worden
        request_params = [*params, ("pageSize", page_size), ("page", page)]

        async with session.get(
            self.EDUCATION_SEARCH_URL,
            params=request_params,
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def __get_organisaties(
        self,
        *,
        page_size: int,
        page: int,
        params: list[tuple[str, Any]],
    ) -> OrganisationSearchResultPayload:
        session = await self.get_session()
        request_params: list[tuple[str, Any]] = [
            *params,
            ("pageSize", page_size),
            ("page", page),
        ]

        async with session.get(
            self.ORGANISATION_SEARCH_URL,
            params=request_params,
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def __get_education_detail(
        self,
        *,
        leerplaats_id: str,
    ) -> EducationDetailPayload:
        session = await self.get_session()
        params: dict[str, Any] = self.get_base_params()
        params["id"] = leerplaats_id

        async with session.get(
            self.EDUCATION_DETAIL_URL,
            params=params,
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def __get_study_locations(
        self,
        *,
        crebocode: int,
        lat: float,
        lon: float,
    ) -> list[StudyLocationResultPayload]:
        session = await self.get_session()
        params: dict[str, Any] = {
            "crebo": crebocode,
            "lat": lat,
            "lon": lon,
        }

        async with session.get(
            self.STUDY_LOCATIONS_URL,
            params=params,
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def __get_organization_detail(
        self,
        *,
        organization_id: str,
    ) -> OrganisationDetailPayload:
        session = await self.get_session()
        params: dict[str, Any] = self.get_base_params()
        params["id"] = organization_id

        async with session.get(
            self.ORGANIZATION_DETAIL_URL,
            params=params,
        ) as resp:
            resp.raise_for_status()
            data: OrganisationDetailPayload = await resp.json()
            return data

    async def zoek_organisaties(
        self,
        *,
        crebocode: int | None = None,
        plaats_postcode: str | None = None,
        straal: Straal | int = Straal.KM_15,
        locatie_type: LocatieType | None = None,
        niveau: Niveau | None = None,
        organisatie: str | None = None,
        sortering: Sortering | None = None,
        alleen_zonder_leerplaatsen: bool = False,
        buitenland: bool = False,
        leerweg: Leerweg | None = None,
        filters: EducatieFilters | None = None,
        limiet: int | None = 20,
        met_details: bool = False,
    ) -> list[Organisatie] | list[OrganisationDetail]:
        """Zoek organisaties op basis van locatie en opleiding.

        Parameters
        ----------
        plaats_postcode: str | None
            Plaats of postcode voor het zoeken van organisaties. Standaard op ``None`` voor
            landelijke zoekopdracht.
        crebocode: int | None
            CREBO-code van de opleiding waarvoor organisaties gezocht worden.
            Standaard ``None`` voor alle erkende leerbedrijven.
        straal: Straal | int
            Zoekstraal rond de opgegeven locatie in kilometers.
            Dit is standaard `Straal.KM_15`.
        locatie_type: LocatieType | None
            Soort zoekgebied van ``plaats_postcode`` (plaats of postcode).
            Zoeken op regio wordt door de API niet ondersteund voor organisaties.
        niveau: Niveau | None
            Opleidingsniveau. Dit is standaard `None`.
        organisatie: str | None
            (Deel van) de naam van de organisatie. Zie ook ``zoek_organisatienamen``.
        sortering: Sortering | None
            Sorteervolgorde van de resultaten. Dit is standaard `None` (relevantie).
        alleen_zonder_leerplaatsen: bool
            Alleen erkende leerbedrijven die op dit moment géén open leerplaatsen
            hebben (zoals "Erkende bedrijven met mogelijk een plek" op de website).
            Dit is standaard `False`.
        buitenland: bool
            Alleen buitenlandse leerbedrijven. Dit is standaard `False`.
        leerweg: Leerweg | None
            Wordt door de API genegeerd bij het zoeken naar organisaties; alleen
            behouden voor compatibiliteit.
        filters: EducatieFilters | None
            Aanvullende filters, zoals bedrijfssoort, bedrijfsgrootte, sector en land.
        limiet: int | None
            Maximum aantal organisaties om te retourneren.
            Standaard is 20. Dit werkt veel sneller dan None.

            WAARSCHUWING: Wanneer dit op `None` is ingesteld, probeert het systeem
            ALLE resultaten op te halen zonder limiet. Dit kan EXTREEM TRAAG zijn,
            afhankelijk van het aantal beschikbare organisaties en of details worden
            opgehaald. Voor grote zoekresultaten kan dit enkele minuten tot uren duren.
            Gebruik altijd een redelijk getal (bijv. 20-100) voor productiegebruik.
        met_details: bool
            Bepaalt of gedetailleerde informatie wordt opgehaald voor elke organisatie.
            Wanneer `True`, wordt voor elke organisatie een extra API-aanroep gedaan om
            uitgebreide informatie op te halen zoals telefoonnummer, contactpersonen,
            erkenningen en leerplaatsen. Wanneer `False`, worden alleen basisgegevens
            geretourneerd zoals naam, adres en website.
            Dit is standaard `False`.

        Returns
        -------
        list[Organisatie] | list[OrganisationDetail]
            Lijst van organisaties (basis) of gedetailleerde organisaties.
        """
        base = self.get_base_params(
            niveau=niveau,
            plaats_postcode=plaats_postcode,
            straal=straal,
            crebocode=crebocode,
            locatie_type=locatie_type,
            sortering=sortering,
        )
        params: list[tuple[str, Any]] = list(base.items())
        if organisatie is not None:
            params.append(("organisatie", organisatie))
        if alleen_zonder_leerplaatsen:
            # Alleen 0 is een geldige waarde; zonder parameter krijg je alle leerbedrijven
            params.append(("aantalLeerplaatsen", 0))
        if buitenland:
            params.append(("buitenland", "true"))
        if leerweg is not None:
            params.append(("leerweg", leerweg.value))
        if filters is not None:
            # Add filter params, excluding potential duplicate leerweg
            params.extend((k, v) for (k, v) in filters.to_params() if k != "leerweg" or leerweg is None)

        requestor: MinimalCallable[OrganisationSearchResultPayload] = partial(
            self.__get_organisaties,
            params=params,
        )
        paginator: Paginator[OrganizationSearchResultItemPayload, OrganisationSearchResultPayload] = Paginator(
            requester=requestor,
            limit=limiet,
            # Bij een pageSize > 20 geeft de API maar 10 items terug
            max_page_size=20,
            items_key="items",
        )
        results: list[OrganizationSearchResultItemPayload] = await paginator.collect()

        if met_details:
            # Fetch detailed info for each organization
            detail_tasks = [self.haal_organisatie_detail(organisatie_id=item["id"]) for item in results]
            return await asyncio.gather(*detail_tasks)

        return [Organisatie(item) for item in results]

    async def zoek_educaties(
        self,
        *,
        niveau: Niveau,
        crebocode: int,
        plaats_postcode: str | None = None,
        straal: Straal | int = Straal.KM_15,
        locatie_type: LocatieType | None = None,
        regio: Regio | str | None = None,
        sortering: Sortering | None = None,
        buitenlandse_bedrijven: bool | None = None,
        educatie_type: EducatieZoekType | None = None,
        filters: EducatieFilters | None = None,
        limiet: int | None = 20,
        met_details: bool = False,
    ) -> list[Educatie] | list[EducationDetail]:
        """Zoek educaties (leerplaatsen) op basis van locatie en opleiding.

        Parameters
        ----------
        niveau: Niveau
            Opleidingsniveau (1, 2, 3, of 4) waarvoor educaties gezocht worden.
        plaats_postcode: str | None
            Plaats of postcode voor het zoeken van educaties.
        crebocode: int
            CREBO-code van de opleiding waarvoor leerplaatsen gezocht worden.
        straal: Straal | int
            Zoekstraal rond de opgegeven locatie in kilometers.
            Dit is standaard `Straal.KM_15`.
        locatie_type: LocatieType | None
            Soort zoekgebied. Gebruik `LocatieType.REGIO` samen met ``regio``.
            Dit is standaard `None`.
        regio: Regio | str | None
            De regio (bijv. `Regio.GROOT_AMSTERDAM`) of het ID ervan. Zoekt in de hele regio in plaats
            van rond ``plaats_postcode``. Dit is standaard `None`.
        sortering: Sortering | None
            Sorteervolgorde van de resultaten. Dit is standaard `None` (relevantie).
        buitenlandse_bedrijven: bool | None
            Bepaalt of buitenlandse bedrijven worden meegenomen in de zoekresultaten.
            Wanneer `True`, worden buitenlandse bedrijven getoond.
            Wanneer `False`, worden alleen Nederlandse bedrijven getoond.
            Dit is standaard `None` (API default gedrag).
        educatie_type: EducatieSearchType | None
            Type educatie om te filteren op specifieke educatievormen.
            Dit is standaard `None` (alle types).
        filters: EducatieFilters | None
            Aanvullende filters voor de zoekopdracht zoals kenmerken, vergoedingen,
            leerwegen en andere specifieke criteria.
            Dit is standaard `None` (geen extra filters).
        limiet: int | None
            Maximum aantal educaties om te retourneren.
            Standaard is 20. Dit werkt veel sneller dan None.

            WAARSCHUWING: Wanneer dit op `None` is ingesteld, probeert het systeem
            ALLE resultaten op te halen zonder limiet. Dit kan EXTREEM TRAAG zijn,
            afhankelijk van het aantal beschikbare leerplaatsen en of details worden
            opgehaald. Voor grote zoekresultaten kan dit enkele minuten tot uren duren.
            Gebruik altijd een redelijk getal (bijv. 20-100) voor productiegebruik.
        met_details: bool
            Bepaalt of gedetailleerde informatie wordt opgehaald voor elke educatie.
            Wanneer `True`, wordt voor elke educatie een extra API-aanroep gedaan om
            uitgebreide informatie op te halen zoals omschrijving, contactgegevens,
            vaardigheden, kerntaken en media. Wanneer `False`, worden alleen basisgegevens
            geretourneerd zoals titel, organisatie en adres.
            Dit is standaard `False`.

        Returns
        -------
        list[Educatie] | list[EducationDetail]
            Lijst van educaties (basis) of gedetailleerde educaties.
        """
        params: dict[str, Any] = self.get_base_params(
            niveau=niveau,
            plaats_postcode=plaats_postcode,
            straal=straal,
            crebocode=crebocode,
            locatie_type=LocatieType.REGIO if regio is not None and locatie_type is None else locatie_type,
            sortering=sortering,
        )
        tuple_params: list[tuple[str, Any]] = []
        if regio is not None:
            params["regio"] = regio.value if isinstance(regio, Regio) else regio
        if educatie_type is not None:
            params["type"] = educatie_type.value
        if buitenlandse_bedrijven is not None:
            params["buitenlandseBedrijven"] = str(buitenlandse_bedrijven).lower()
        if filters:
            tuple_params += filters.to_params()

        tuple_params = list(params.items()) + tuple_params

        requestor: MinimalCallable[EducatieSearchResultPayload] = partial(
            self.__get_educations,
            params=tuple_params,
        )
        paginator: Paginator[EducatieSearchResultItemPayload, EducatieSearchResultPayload] = Paginator(
            requester=requestor,
            limit=limiet,
            # education-search accepteert grote pagina's (organization-search max 20)
            max_page_size=100,
            items_key="items",
        )
        results: list[EducatieSearchResultItemPayload] = await paginator.collect()
        if met_details:
            detail_tasks = [self.haal_educatie_detail(leerplaats_id=item["leerplaatsId"]) for item in results]
            return await asyncio.gather(*detail_tasks)

        return [Educatie(item) for item in results]

    async def __get_opleiding_suggesties(
        self,
        *,
        niveau: Niveau,
        term: str | None,
        page_size: int,
    ) -> OpleidingSuggestiePayload:
        session = await self.get_session()
        params: dict[str, Any] = self.get_base_params(niveau=niveau)  # opleidingsniveau
        params["pageSize"] = page_size
        if term is not None:
            params["term"] = term

        async with session.get(
            self.OPLEIDING_SUGGESTIES_URL,
            params=params,
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def zoek_opleidingen(
        self,
        *,
        niveau: Niveau,
        term: str | None = None,
        limiet: int = 1000,
    ) -> OpleidingSuggestie:
        """Zoek naar opleiding suggesties voor een specifiek niveau.

        Parameters
        ----------
        niveau: Niveau
            Opleidingsniveau (1, 2, 3, of 4) waarvoor suggesties worden opgehaald.
        term: str | None
            Zoekterm om opleidingen te filteren op naam of omschrijving.
            Wanneer `None`, worden alle opleidingen voor het niveau geretourneerd.
            Dit is standaard `None`.
        limiet: int
            Maximum aantal suggesties om te retourneren.
            Dit is standaard `1000`.

        Returns
        -------
        OpleidingSuggestie
            Opleidingssuggesties voor het opgegeven niveau.
        """
        data: OpleidingSuggestiePayload = await self.__get_opleiding_suggesties(
            niveau=niveau,
            term=term,
            page_size=limiet,
        )
        return OpleidingSuggestie(data)

    async def haal_educatie_detail(
        self,
        *,
        leerplaats_id: str,
    ) -> EducationDetail:
        """Haal gedetailleerde informatie op voor een specifieke educatie (leerplaats).

        Parameters
        ----------
        leerplaats_id: str
            Unieke ID van de leerplaats.

        Returns
        -------
        EducationDetail
            Gedetailleerde informatie over de educatie.
        """
        data: EducationDetailPayload = await self.__get_education_detail(leerplaats_id=leerplaats_id)
        return EducationDetail(data)

    async def haal_studie_locaties(
        self,
        *,
        crebocode: int,
        lat: float,
        lon: float,
    ) -> list[StudyLocation]:
        """Haal studielocaties op voor een gegeven crebocode en coördinaten.

        Parameters
        ----------
        crebocode: int
            CREBO-code van de opleiding.
        lat: float
            Breedtegraad van de locatie.
        lon: float
            Lengtegraad van de locatie.

        Returns
        -------
        list[StudyLocation]
            Lijst van studielocaties in de buurt van de opgegeven coördinaten.
        """
        results = await self.__get_study_locations(
            crebocode=crebocode,
            lat=lat,
            lon=lon,
        )
        return [StudyLocation(item) for item in results]

    async def haal_organisatie_detail(
        self,
        *,
        organisatie_id: str,
    ) -> OrganisationDetail:
        """Haal gedetailleerde informatie op voor een specifieke organisatie.

        Parameters
        ----------
        organisatie_id: str
            Unieke ID van de organisatie.

        Returns
        -------
        OrganisationDetail
            Gedetailleerde informatie over de organisatie.
        """
        data: OrganisationDetailPayload = await self.__get_organization_detail(organization_id=organisatie_id)
        return OrganisationDetail(data)

    async def haal_regios(self) -> list[RegioInfo]:
        """Haal alle regio's op.

        Returns
        -------
        list[RegioInfo]
            Alle regio's zoals de API ze nu teruggeeft. Zie ook de enum :class:`Regio`.
        """
        session = await self.get_session()
        async with session.get(self.REGIOS_URL) as resp:
            resp.raise_for_status()
            data: list[RegioPayload] = await resp.json()
            return [RegioInfo(item) for item in data]

    async def zoek_organisatienamen(self, *, term: str) -> list[str]:
        """Zoek organisatienamen die overeenkomen met een zoekterm.

        Parameters
        ----------
        term: str
            (Deel van) de naam van de organisatie, minimaal 2 tekens.

        Returns
        -------
        list[str]
            Gevonden organisatienamen.
        """
        session = await self.get_session()
        async with session.get(self.ORGANISATIE_SUGGESTIES_URL, params={"term": term}) as resp:
            resp.raise_for_status()
            data: OrganisatieSuggestiePayload = await resp.json()
            return [item["value"] for item in data.get("items") or []]

    async def haal_filter_opties(
        self,
        *,
        organisaties: bool = False,
        crebocode: int | None = None,
        niveau: Niveau | None = None,
        plaats_postcode: str | None = None,
        straal: Straal | int | None = None,
        locatie_type: LocatieType | None = None,
        regio: Regio | str | None = None,
        filters: EducatieFilters | None = None,
    ) -> list[ZoekFilter]:
        """Haal de beschikbare filteropties (met aantallen) op voor een zoekopdracht.

        Dit zijn dezelfde opties als in het filtermenu van de website, zoals alle
        bedrijfssoorten, bedrijfsgroottes, sectoren, landen, leerwegen en vergoedingen.

        Parameters
        ----------
        organisaties: bool
            ``True`` voor de filters van leerbedrijven, ``False`` voor die van stages.
        crebocode: int | None
            CREBO-code van de opleiding.
        niveau: Niveau | None
            Opleidingsniveau.
        plaats_postcode: str | None
            Plaats of postcode. ``None`` voor heel Nederland.
        straal: Straal | int | None
            Zoekstraal in kilometers. Standaard `Straal.KM_15` wanneer een plaats is opgegeven.
        locatie_type: LocatieType | None
            Soort zoekgebied.
        regio: Regio | str | None
            De regio of het ID ervan (alleen voor stages).
        filters: EducatieFilters | None
            Filters die al toegepast moeten worden.

        Returns
        -------
        list[ZoekFilter]
            Filters met hun opties. :attr:`ZoekFilter.id` is de naam van de query parameter.
        """
        if plaats_postcode is not None and straal is None:
            straal = Straal.KM_15
        params: dict[str, Any] = self.get_base_params(
            niveau=niveau,
            plaats_postcode=plaats_postcode,
            straal=straal,
            crebocode=crebocode,
            locatie_type=LocatieType.REGIO if regio is not None and locatie_type is None else locatie_type,
        )
        if regio is not None:
            params["regio"] = regio.value if isinstance(regio, Regio) else regio
        request_params: list[tuple[str, Any]] = [*params.items(), *(filters.to_params() if filters else [])]
        url = self.ORGANISATION_SEARCH_URL if organisaties else self.EDUCATION_SEARCH_URL

        session = await self.get_session()
        async with session.get(url, params=[*request_params, ("pageSize", 1), ("page", 1)]) as resp:
            resp.raise_for_status()
            data: OrganisationSearchResultPayload | EducatieSearchResultPayload = await resp.json()
            return [ZoekFilter(f) for f in data.get("filters") or []]

    async def haal_filter_definities(self) -> list[FilterDefinitie]:
        """Haal de filterdefinities op zoals ingesteld in het CMS van de website.

        Returns
        -------
        list[FilterDefinitie]
            Alle filters met hun parameternaam, label, type en vaste opties.
        """
        session = await self.get_session()
        async with session.get(self.UMBRACO_FILTERS_URL) as resp:
            resp.raise_for_status()
            data: list[FilterDefinitiePayload] = await resp.json()
            return [FilterDefinitie(item) for item in data]

    async def haal_pagina(self, *, route: str) -> dict[str, Any]:
        """Haal de ruwe CMS-inhoud van een pagina op, bijv. ``"/leerbedrijven"`` of ``"/sollicitatie"``.

        Parameters
        ----------
        route: str
            Pad van de pagina op stagemarkt.nl.

        Returns
        -------
        dict[str, Any]
            De ruwe Umbraco-inhoud. Zoekpagina's (``__typename == "SearchPage"``) bevatten
            o.a. de getoonde filters en sorteeropties.
        """
        session = await self.get_session()
        async with session.get(self.UMBRACO_CONTENT_URL, params={"route": route}) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def haal_vertalingen(self) -> dict[str, dict[str, str]]:
        """Haal alle teksten van de website op.

        Returns
        -------
        dict[str, dict[str, str]]
            Per categorie (bijv. ``"forms"``) een mapping van naam naar tekst.
        """
        session = await self.get_session()
        async with session.get(self.UMBRACO_TRANSLATIONS_URL) as resp:
            resp.raise_for_status()
            data: VertalingenPayload = await resp.json()
            return {
                categorie["localeCategory"]: {item["name"]: item["value"] for item in categorie.get("locales") or []}
                for categorie in data.get("locales") or []
            }

    async def haal_formulier(self, *, formulier: FormulierSoort | str) -> Formulier:
        """Haal de definitie (velden) van een formulier op.

        Parameters
        ----------
        formulier: FormulierSoort | str
            Het formulier, bijv. `FormulierSoort.SOLLICITATIE`, of het ID ervan.

        Returns
        -------
        Formulier
            De velden van het formulier.
        """
        session = await self.get_session()
        formulier_id = formulier.value if isinstance(formulier, FormulierSoort) else formulier
        async with session.get(self.UMBRACO_FORM_URL, params={"id": formulier_id}) as resp:
            resp.raise_for_status()
            data: FormulierPayload = await resp.json()
            return Formulier(data)

    async def haal_stage_preview(self, *, token: str) -> StagePreview | None:
        """Haal een voorbeeldweergave van een stage op met een preview-token.

        Parameters
        ----------
        token: str
            Preview-token, zoals in ``https://stagemarkt.nl/stages/preview?token=...``.

        Returns
        -------
        StagePreview | None
            De stage, of ``None`` als het token ongeldig of verlopen is.
        """
        session = await self.get_session()
        async with session.get(self.STAGE_PREVIEW_URL, params={"token": token}) as resp:
            resp.raise_for_status()
            data = self._lees_json(await resp.text())
            if not isinstance(data, dict):
                # De API geeft platte tekst "not-found" terug bij een onbekend token
                return None
            return StagePreview(data)

    async def haal_mail_alert(self, *, mail_guid: str) -> MailAlert:
        """Haal een mail alert op.

        Parameters
        ----------
        mail_guid: str
            De ``mailGuid`` uit de link in een mail alert e-mail
            (``https://stagemarkt.nl/?mailGuid=...``).

        Returns
        -------
        MailAlert
            Het e-mailadres en de opgeslagen zoekopdrachten.
        """
        session = await self.get_session()
        async with session.get(self.MAIL_ALERTS_URL, params={"mailGuid": mail_guid}) as resp:
            resp.raise_for_status()
            data: MailAlertPayload = await resp.json()
            return MailAlert(data)

    def _maak_bestand(self, pad: str | Path) -> FormulierBestandPayload:
        pad = Path(pad)
        if pad.suffix.lower() not in self.BESTAND_EXTENSIES:
            msg = f"{pad.name}: alleen {', '.join(self.BESTAND_EXTENSIES)} bestanden zijn toegestaan."
            raise ValueError(msg)
        inhoud = pad.read_bytes()
        if len(inhoud) > self.MAX_BESTAND_GROOTTE:
            msg = f"{pad.name}: bestand is groter dan 5 MB."
            raise ValueError(msg)
        mime = mimetypes.guess_type(pad.name)[0] or "application/octet-stream"
        return {
            "fileName": pad.name,
            "fileContents": f"data:{mime};base64,{base64.b64encode(inhoud).decode('ascii')}",
        }

    @staticmethod
    def _controleer_toestemming(*, toestemming: bool) -> None:
        if not toestemming:
            msg = "Toestemming (privacyverklaring) is verplicht om een formulier te versturen."
            raise ValueError(msg)

    async def verstuur_formulier(self, *, formulier: FormulierSoort | str, waarden: dict[str, Any]) -> dict[str, Any]:
        """Verstuur een formulier, zoals de website dat doet.

        Let op: dit verstuurt echt een bericht (bijv. een sollicitatie of vraag aan een leerbedrijf).

        Parameters
        ----------
        formulier: FormulierSoort | str
            Het formulier (of het ID ervan).
        waarden: dict[str, Any]
            Waarden per veld-alias (zie :meth:`haal_formulier`).

        Returns
        -------
        dict[str, Any]
            Het antwoord van de server (kan leeg zijn).
        """
        session = await self.get_session()
        # "website" is een honeypot-veld op de website en moet leeg blijven
        formulier_id = formulier.value if isinstance(formulier, FormulierSoort) else formulier
        payload = {"id": formulier_id, "values": {"website": "", **waarden}}
        headers = {"Content-Type": "application/json", "Origin": self.SITE_URL}
        async with session.post(self.FORMS_SUBMIT_URL, json=payload, headers=headers) as resp:
            resp.raise_for_status()
            data = self._lees_json(await resp.text())
            return data if isinstance(data, dict) else {}

    @staticmethod
    def _lees_json(tekst: str) -> dict[str, Any] | list[Any] | str | None:
        """Lees JSON uit een response die ook platte tekst of leeg kan zijn."""
        if not tekst.strip():
            return None
        try:
            return json.loads(tekst)
        except json.JSONDecodeError:
            return tekst

    async def solliciteer(
        self,
        *,
        leerplaats_id: str,
        naam: str,
        email: str,
        telefoonnummer: str,
        motivatie: str,
        toestemming: bool,
        online_cv: str | None = None,
        bestanden: list[str | Path] | None = None,
    ) -> dict[str, Any]:
        """Solliciteer op een stage (formulier op ``/sollicitatie``).

        Parameters
        ----------
        leerplaats_id: str
            ID van de stage (:attr:`Educatie.leerplaats_id`).
        naam: str
            Je naam.
        email: str
            Je e-mailadres.
        telefoonnummer: str
            Je telefoonnummer.
        motivatie: str
            Bericht of motivatie.
        toestemming: bool
            Akkoord met de privacyverklaring; moet ``True`` zijn.
        online_cv: str | None
            Link naar een online CV.
        bestanden: list[str | Path] | None
            CV en/of motivatiebrief (.pdf, .docx, .doc of .txt, max. 5 MB per bestand).

        Returns
        -------
        dict[str, Any]
            Het antwoord van de server.
        """
        self._controleer_toestemming(toestemming=toestemming)
        bijlagen = [self._maak_bestand(b) for b in bestanden or []]
        detail = await self.__get_education_detail(leerplaats_id=leerplaats_id)
        waarden: dict[str, Any] = {
            "naam": naam,
            "emailadres": email,
            "emailadres2": email,
            "telefoonnummer": telefoonnummer,
            "berichtOfMotivatie": motivatie,
            "onlineCV": online_cv or "",
            "cVEnofMotivatiebrief": bijlagen,
            "dataConsent": "True",
            "leerplaatsId": leerplaats_id,
            "contactPersonEmail": detail.get("emailadres") or "",
            "siteType": self.SITE_TYPE,
        }
        return await self.verstuur_formulier(formulier=FormulierSoort.SOLLICITATIE, waarden=waarden)

    async def stel_vraag_over_stage(
        self,
        *,
        leerplaats_id: str,
        naam: str,
        email: str,
        telefoonnummer: str,
        vraag: str,
        toestemming: bool,
    ) -> dict[str, Any]:
        """Stel een vraag over een stage (formulier op ``/contact``).

        Parameters
        ----------
        leerplaats_id: str
            ID van de stage.
        naam: str
            Je naam.
        email: str
            Je e-mailadres.
        telefoonnummer: str
            Je telefoonnummer.
        vraag: str
            Je vraag.
        toestemming: bool
            Akkoord met de privacyverklaring; moet ``True`` zijn.

        Returns
        -------
        dict[str, Any]
            Het antwoord van de server.
        """
        self._controleer_toestemming(toestemming=toestemming)
        detail = await self.__get_education_detail(leerplaats_id=leerplaats_id)
        waarden: dict[str, Any] = {
            "naam": naam,
            "emailadres": email,
            "emailadres2": email,
            "telefoonnummer": telefoonnummer,
            "berichtOfMotivatie": vraag,
            "dataConsent": "True",
            "leerplaatsId": leerplaats_id,
            "contactPersonEmail": detail.get("emailadres") or "",
            "siteType": self.SITE_TYPE,
        }
        return await self.verstuur_formulier(formulier=FormulierSoort.VRAAG_OVER_STAGE, waarden=waarden)

    async def stel_vraag_aan_leerbedrijf(
        self,
        *,
        organisatie_id: str,
        naam: str,
        email: str,
        telefoonnummer: str,
        vraag: str,
        toestemming: bool,
    ) -> dict[str, Any]:
        """Stel een vraag aan een leerbedrijf (formulier op ``/contact-leerbedrijf``).

        Parameters
        ----------
        organisatie_id: str
            ID van de organisatie (:attr:`Organisatie.id`).
        naam: str
            Je naam.
        email: str
            Je e-mailadres.
        telefoonnummer: str
            Je telefoonnummer.
        vraag: str
            Je vraag.
        toestemming: bool
            Akkoord met de privacyverklaring; moet ``True`` zijn.

        Returns
        -------
        dict[str, Any]
            Het antwoord van de server.
        """
        self._controleer_toestemming(toestemming=toestemming)
        detail = await self.__get_organization_detail(organization_id=organisatie_id)
        waarden: dict[str, Any] = {
            "naam": naam,
            "emailadres": email,
            "emailadres2": email,
            "telefoonnummer": telefoonnummer,
            "berichtOfMotivatie": vraag,
            "dataConsent": "True",
            "leerbedrijfId": organisatie_id,
            "contactPersonEmail": detail.get("emailadres") or "",
            "siteType": self.SITE_TYPE,
        }
        return await self.verstuur_formulier(formulier=FormulierSoort.VRAAG_AAN_LEERBEDRIJF, waarden=waarden)

    async def meld_probleem(
        self,
        *,
        leerplaats_id: str,
        toelichting: str,
        naam: str,
        email: str,
        toestemming: bool,
        soort: ProbleemSoort | None = None,
    ) -> dict[str, Any]:
        """Meld dat er iets niet klopt aan een stage (formulier "Klopt iets niet?").

        Parameters
        ----------
        leerplaats_id: str
            ID van de stage.
        toelichting: str
            Uitleg van het probleem.
        naam: str
            Je naam.
        email: str
            Je e-mailadres.
        toestemming: bool
            Akkoord met de privacyverklaring; moet ``True`` zijn.
        soort: ProbleemSoort | None
            Wat er niet klopt.

        Returns
        -------
        dict[str, Any]
            Het antwoord van de server.
        """
        self._controleer_toestemming(toestemming=toestemming)
        waarden: dict[str, Any] = {
            "watKloptErNiet": soort.value if soort is not None else "",
            "berichtOfMotivatie": toelichting,
            "naam": naam,
            "emailadres": email,
            "emailadres2": email,
            "dataConsent": "True",
            "leerplaatsId": leerplaats_id,
            "siteType": self.SITE_TYPE,
        }
        return await self.verstuur_formulier(formulier=FormulierSoort.KLOPT_IETS_NIET, waarden=waarden)

    async def maak_mail_alert(
        self,
        *,
        email: str,
        zoekopdrachten: list[MailAlertItem],
        toestemming: bool,
        nieuwsbrief: bool = False,
    ) -> dict[str, Any]:
        """Maak een mail alert aan voor één of meer zoekopdrachten.

        Parameters
        ----------
        email: str
            E-mailadres waarop je meldingen wilt ontvangen.
        zoekopdrachten: list[MailAlertItem]
            Zoekopdrachten om op te slaan.
        toestemming: bool
            Akkoord met de privacyverklaring; moet ``True`` zijn.
        nieuwsbrief: bool
            Ook inschrijven voor de nieuwsbrief. Standaard ``False``.

        Returns
        -------
        dict[str, Any]
            Het antwoord van de server.
        """
        self._controleer_toestemming(toestemming=toestemming)
        if not zoekopdrachten:
            msg = "Er moet minimaal één zoekopdracht opgegeven worden."
            raise ValueError(msg)
        waarden: dict[str, Any] = {
            "email": email,
            "dataConsent": "True",
            "items": [item.to_payload() for item in zoekopdrachten],
        }
        if nieuwsbrief:
            waarden["newsletter"] = "True"
        return await self.verstuur_formulier(formulier=FormulierSoort.MAIL_ALERT_AANMAKEN, waarden=waarden)

    async def wijzig_mail_alert(
        self,
        *,
        mail_guid: str,
        verwijder: list[MailAlertItem] | None = None,
        nieuwsbrief: bool | None = None,
    ) -> dict[str, Any]:
        """Verwijder zoekopdrachten uit een mail alert en/of wijzig de nieuwsbriefinschrijving.

        Parameters
        ----------
        mail_guid: str
            De ``mailGuid`` uit de link in een mail alert e-mail.
        verwijder: list[MailAlertItem] | None
            Zoekopdrachten om te verwijderen (uit :attr:`MailAlert.items`).
        nieuwsbrief: bool | None
            Nieuwe nieuwsbriefinschrijving; ``None`` laat deze ongewijzigd.

        Returns
        -------
        dict[str, Any]
            Het antwoord van de server.
        """
        alert = await self.haal_mail_alert(mail_guid=mail_guid)
        if nieuwsbrief is None:
            nieuwsbrief = alert.nieuwsbrief
        waarden: dict[str, Any] = {
            "email": alert.email,
            "dataConsent": "True",
            "itemsToDelete": [item.to_payload() for item in verwijder or []],
        }
        if nieuwsbrief:
            waarden["newsletter"] = "True"
        return await self.verstuur_formulier(formulier=FormulierSoort.MAIL_ALERT_WIJZIGEN, waarden=waarden)
