from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Self, overload

from .enums import EducatieZoekType, Straal
from .internals.http import HTTPClient

if TYPE_CHECKING:
    from aiohttp import ClientSession

    from .enums import Leerweg, Niveau
    from .models import (
        Educatie,
        EducatieFilters,
        EducationDetail,
        LocatieSuggestie,
        OpleidingSuggestie,
        Organisatie,
        OrganisationDetail,
        StudyLocation,
    )


class StagemarktClient:
    """High-level client voor de Stagemarkt API.

    Deze client biedt een handig interface voor het zoeken en ophalen van
    stage plaatsen, organisaties en studielocaties in Nederland.

    Parameters
    ----------
    session: ClientSession | None
        Een optionele aiohttp ClientSession om te hergebruiken voor HTTP-verzoeken.
    """

    def __init__(self, session: ClientSession | None = None) -> None:
        self.__http: HTTPClient = HTTPClient(session=session)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.afsluiten()

    async def afsluiten(self) -> None:
        """Sluit de client verbinding af.

        Dit zou aangeroepen moeten worden wanneer je klaar bent met het
        gebruiken van de client om resources correct op te ruimen.
        """
        await self.__http.close()

    @overload
    async def zoek_stages(
        self,
        *,
        niveau: Niveau,
        plaats: str,
        crebocode: int,
        straal: Straal = ...,
        limiet: int | None = ...,
        buitenlandse_bedrijven: bool = ...,
        met_details: Literal[False] = ...,
        filters: EducatieFilters | None = ...,
    ) -> list[Educatie]: ...

    @overload
    async def zoek_stages(
        self,
        *,
        niveau: Niveau,
        plaats: str,
        crebocode: int,
        straal: Straal = ...,
        limiet: int | None = ...,
        buitenlandse_bedrijven: bool = ...,
        met_details: Literal[True] = ...,
        filters: EducatieFilters | None = ...,
    ) -> list[EducationDetail]: ...

    async def zoek_stages(
        self,
        *,
        niveau: Niveau,
        plaats: str,
        crebocode: int,
        straal: Straal | int = Straal.KM_25,
        limiet: int | None = 20,
        educatie_type: EducatieZoekType | None = None,
        buitenlandse_bedrijven: bool = False,
        met_details: bool = False,
        filters: EducatieFilters | None = None,
    ) -> list[Educatie] | list[EducationDetail]:
        """Zoek naar stage plaatsen.

        Parameters
        ----------
        niveau: Niveau
            Het onderwijsniveau waarvoor gezocht moet worden (MBO 1, 2, 3 of 4).
        plaats: str
            De plaats/stad waar gezocht moet worden (bijv. "Amsterdam").
        crebocode: int
            De CREBO code van de opleiding.
        straal: Straal | int
            De zoekradius in kilometers (standaard: 25km). Dit kan een Straal enum zijn of een integer waarde.
        limiet: int
            Maximum aantal resultaten (standaard: 20).
        educatie_type: EducatieZoekType | None
            Het type educatie om naar te zoeken (stage, leerbaan, etc.). Standaard ``None`` voor alle types.
        buitenlandse_bedrijven: bool
            Of ook buitenlandse bedrijven moeten worden meegenomen in de zoekresultaten (standaard: False).
        met_details: bool
            Of gedetailleerde informatie moet worden opgehaald (standaard: False).
            Wanneer True, wordt voor elke stage extra informatie opgehaald.
        filters: EducatieFilters | None
            Aanvullende filters. Standaard ``None``.

        Returns
        -------
        list[Educatie] | list[EducationDetail]
            Lijst van stage plaatsen. Type hangt af van met_details parameter.
        """
        return await self.__http.zoek_educaties(
            niveau=niveau,
            plaats_postcode=plaats,
            crebocode=crebocode,
            straal=straal,
            educatie_type=educatie_type,
            buitenlandse_bedrijven=buitenlandse_bedrijven,
            met_details=met_details,
            limiet=limiet,
            filters=filters,
        )

    async def haal_stage_detail(self, leerplaats_id: str) -> EducationDetail:
        """Haal gedetailleerde informatie over een specifieke stage op.

        Parameters
        ----------
        leerplaats_id: str
            De unieke identifier van de stage.

        Returns
        -------
        EducationDetail
            Gedetailleerde informatie over de stage.
        """
        return await self.__http.haal_educatie_detail(leerplaats_id=leerplaats_id)

    @overload
    async def zoek_organisaties(
        self,
        *,
        plaats: str,
        crebocode: int,
        straal: Straal = ...,
        leerweg: Leerweg | None = ...,
        filters: EducatieFilters | None = ...,
        limiet: int = ...,
        met_details: Literal[False] = ...,
    ) -> list[Organisatie]: ...

    @overload
    async def zoek_organisaties(
        self,
        *,
        plaats: str,
        crebocode: int,
        straal: Straal = ...,
        leerweg: Leerweg | None = ...,
        filters: EducatieFilters | None = ...,
        limiet: int = ...,
        met_details: Literal[True] = ...,
    ) -> list[OrganisationDetail]: ...

    async def zoek_organisaties(
        self,
        *,
        plaats: str,
        crebocode: int,
        straal: Straal = Straal.KM_25,
        leerweg: Leerweg | None = None,
        filters: EducatieFilters | None = None,
        limiet: int = 20,
        met_details: bool = False,
    ) -> list[Organisatie] | list[OrganisationDetail]:
        """Zoek naar organisaties die stages aanbieden.

        Parameters
        ----------
        plaats: str
            De plaats/stad waar gezocht moet worden.
        crebocode: int
            De CREBO code van de opleiding.
        straal: Straal
            De zoekradius in kilometers (standaard: 25km). Dit kan een Straal enum zijn of een integer waarde.
        limiet: int
            Maximum aantal resultaten (standaard: 20).
        met_details: bool
            Of gedetailleerde informatie moet worden opgehaald (standaard: False).
            Wanneer True, wordt voor elke organisatie extra informatie opgehaald.

        Returns
        -------
        list[Organisatie] | list[OrganisationDetail]
            Lijst van organisaties. Type hangt af van met_details parameter.
        """
        return await self.__http.zoek_organisaties(
            plaats_postcode=plaats,
            crebocode=crebocode,
            straal=straal,
            leerweg=leerweg,
            filters=filters,
            met_details=met_details,
            limiet=limiet,
        )

    async def haal_organisatie_detail(self, organisatie_id: str) -> OrganisationDetail:
        """Haal gedetailleerde informatie over een specifieke organisatie op.

        Parameters
        ----------
        organisatie_id: str
            De unieke identifier van de organisatie.

        Returns
        -------
        OrganisationDetail
            Gedetailleerde informatie over de organisatie.
        """
        return await self.__http.haal_organisatie_detail(organisatie_id=organisatie_id)

    async def zoek_locaties(self, term: str) -> LocatieSuggestie:
        """Zoek naar locatie suggesties.

        Parameters
        ----------
        term: str
            De zoekterm (bijv. plaatsnaam of postcode).

            Het is de bedoeling om suggesties te krijgen voor locaties die overeenkomen met de opgegeven term.

        Returns
        -------
        LocatieSuggestie
            Locatie suggesties die match met de zoekterm.
        """
        return await self.__http.haal_locaties(term=term)

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
            Het onderwijsniveau waarvoor suggesties opgehaald moeten worden.
        term: str | None
            Zoekterm om cursussen op naam te filteren (optioneel).

            Het is de bedoeling om suggesties te krijgen voor opleidingen die overeenkomen met de opgegeven term.
            Als geen term wordt opgegeven, worden <limiet> opleidingen voor het gegeven niveau opgehaald.
        limiet: int
            Maximum aantal suggesties (standaard: 1000).

        Returns
        -------
        OpleidingSuggestie
            Opleiding suggesties voor het gegeven niveau.
        """
        return await self.__http.zoek_opleidingen(
            niveau=niveau,
            term=term,
            limiet=limiet,
        )

    async def zoek_studie_locaties(
        self,
        *,
        crebocode: int,
        lat: float,
        lon: float,
    ) -> list[StudyLocation]:
        """Zoek studielocaties voor een specifieke cursus in de buurt van coördinaten.

        Parameters
        ----------
        crebocode: int
            De CREBO code van de cursus.
        lat: float
            Breedtegraad van het zoekcentrum.
        lon: float
            Lengtegraad van het zoekcentrum.

        Returns
        -------
        list[StudyLocation]
            Lijst van studielocaties in de buurt van de gegeven coördinaten.
        """
        return await self.__http.haal_studie_locaties(
            crebocode=crebocode,
            lat=lat,
            lon=lon,
        )
