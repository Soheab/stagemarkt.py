from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Protocol,
    TypedDict,
)
import asyncio
from functools import partial
import random

import aiohttp

from ..enums import EducatieZoekType, Leerweg, Niveau, Straal
from ..models import (
    Educatie,
    EducatieFilters,
    EducationDetail,
    LocatieSuggestie,
    OpleidingSuggestie,
    Organisatie,
    OrganisationDetail,
    StudyLocation,
)

if TYPE_CHECKING:
    from _types.educatie_detail import EducationDetail as EducationDetailPayload
    from _types.educatie_search import (
        EducatieSearchResult as EducatieSearchResultPayload,
        EducatieSearchResultItem as EducatieSearchResultItemPayload,
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
    STUDY_LOCATIONS_URL = f"{BASE_URL}/study-locations"
    EDUCATION_DETAIL_URL = f"{BASE_URL}/education-detail"
    ORGANIZATION_DETAIL_URL = f"{BASE_URL}/organization-detail"

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
    ) -> dict[str, Any]:
        base: dict[str, Any] = {
            "siteId": "STAGEMARKT",
        }
        if niveau is not None:
            base["niveau"] = niveau.value
        if plaats_postcode is not None:
            base["plaatsPostcode"] = plaats_postcode
        if straal is not None:
            base["range"] = straal if isinstance(straal, int) else straal.value
        if crebocode is not None:
            base["crebocode"] = crebocode
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

    async def haal_locaties(self, *, term: str) -> LocatieSuggestie:
        """Haal locatiesuggesties op voor een gegeven zoekterm.

        Parameters
        ----------
        term: str
            Zoekterm voor locaties (bijv. plaatsnaam of postcode).

        Returns
        -------
        LocatieSuggestie
            Locatiesuggesties die overeenkomen met de zoekterm.
        """
        session = await self.get_session()
        params: dict[str, Any] = self.get_base_params()
        params["term"] = term

        async with session.get(self.LOCATIE_SUGGESTIES_URL, params=params) as resp:
            if resp.status == 500:
                # Soms geeft de API een 500 terug bij lege resultaten
                return LocatieSuggestie({"status": 500, "body": {"data": []}})

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
        plaats_postcode: str,
        crebocode: int,
        straal: Straal = Straal.KM_15,
        leerweg: Leerweg | None = None,
        filters: EducatieFilters | None = None,
        limiet: int | None = 20,
        met_details: bool = False,
    ) -> list[Organisatie] | list[OrganisationDetail]:
        """Zoek organisaties op basis van locatie en opleiding.

        Parameters
        ----------
        plaats_postcode: str
            Plaats of postcode voor het zoeken van organisaties.
        crebocode: int
            CREBO-code van de opleiding waarvoor organisaties gezocht worden.
        straal: Straal
            Zoekstraal rond de opgegeven locatie in kilometers.
            Dit is standaard `Straal.KM_15`.
        leerweg: Leerweg | None
            Type leerweg om organisaties te filteren (bijv. BOL of BBL).
            Dit is standaard `None` (alle leerwegen).
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
            plaats_postcode=plaats_postcode,
            straal=straal,
            crebocode=crebocode,
        )
        params: list[tuple[str, Any]] = list(base.items())
        if leerweg is not None:
            params.append(("learningPath", leerweg.value))
        if filters is not None:
            # Add filter params, excluding potential duplicate learningPath
            params.extend((k, v) for (k, v) in filters.to_params() if k != "learningPath")

        requestor: MinimalCallable[OrganisationSearchResultPayload] = partial(
            self.__get_organisaties,
            params=params,
        )
        paginator: Paginator[OrganizationSearchResultItemPayload, OrganisationSearchResultPayload] = Paginator(
            requester=requestor,
            limit=limiet,
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
        plaats_postcode: str,
        crebocode: int,
        straal: Straal | int = Straal.KM_15,
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
        plaats_postcode: str
            Plaats of postcode voor het zoeken van educaties.
        crebocode: int
            CREBO-code van de opleiding waarvoor leerplaatsen gezocht worden.
        straal: Straal | int
            Zoekstraal rond de opgegeven locatie in kilometers.
            Dit is standaard `Straal.KM_15`.
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
        )
        tuple_params: list[tuple[str, Any]] = []
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
            items_key="items",
        )
        results: list[EducatieSearchResultItemPayload] = await paginator.collect()

        if met_details:
            # Fetch detailed info for each education
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
        params: dict[str, Any] = self.get_base_params(niveau=niveau)
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
