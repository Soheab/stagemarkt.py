from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Self, overload

from .enums import EducatieZoekType, Straal
from .internals.http import HTTPClient

if TYPE_CHECKING:
    from typing import Any
    from pathlib import Path

    from aiohttp import ClientSession

    from .enums import FormulierSoort, Leerweg, LocatieType, Niveau, ProbleemSoort, Regio, Sortering
    from .models import (
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
        crebocode: int,
        plaats: str | None = ...,
        straal: Straal | int = ...,
        locatie_type: LocatieType | None = ...,
        regio: Regio | str | None = ...,
        sortering: Sortering | None = ...,
        limiet: int | None = ...,
        educatie_type: EducatieZoekType | None = ...,
        buitenlandse_bedrijven: bool = ...,
        met_details: Literal[False] = ...,
        filters: EducatieFilters | None = ...,
    ) -> list[Educatie]: ...

    @overload
    async def zoek_stages(
        self,
        *,
        niveau: Niveau,
        crebocode: int,
        plaats: str | None = ...,
        straal: Straal | int = ...,
        locatie_type: LocatieType | None = ...,
        regio: Regio | str | None = ...,
        sortering: Sortering | None = ...,
        limiet: int | None = ...,
        educatie_type: EducatieZoekType | None = ...,
        buitenlandse_bedrijven: bool = ...,
        met_details: Literal[True] = ...,
        filters: EducatieFilters | None = ...,
    ) -> list[EducationDetail]: ...

    async def zoek_stages(
        self,
        *,
        niveau: Niveau,
        crebocode: int,
        plaats: str | None = None,
        straal: Straal | int = Straal.KM_25,
        locatie_type: LocatieType | None = None,
        regio: Regio | str | None = None,
        sortering: Sortering | None = None,
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
        plaats: str | None
            De plaats/stad of postcode waar gezocht moet worden (bijv. "Amsterdam"). Standaard op ``None`` voor
            landelijke zoekopdracht.
        crebocode: int
            De CREBO code van de opleiding.
        straal: Straal | int
            De zoekradius in kilometers (standaard: 25km). Dit kan een Straal enum zijn of een integer waarde.
        locatie_type: LocatieType | None
            Soort zoekgebied van ``plaats`` (plaats, postcode of regio). Standaard ``None``.
        regio: Regio | str | None
            De regio (bijv. `Regio.GROOT_AMSTERDAM`) of het ID ervan. Zoekt in de hele regio in plaats van rond ``plaats``.
        sortering: Sortering | None
            Sorteervolgorde van de resultaten. Standaard ``None`` (relevantie).
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
            locatie_type=locatie_type,
            regio=regio,
            sortering=sortering,
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
        crebocode: int | None = ...,
        *,
        plaats: str | None = ...,
        straal: Straal | int = ...,
        locatie_type: LocatieType | None = ...,
        niveau: Niveau | None = ...,
        organisatie: str | None = ...,
        sortering: Sortering | None = ...,
        alleen_zonder_leerplaatsen: bool = ...,
        buitenland: bool = ...,
        leerweg: Leerweg | None = ...,
        filters: EducatieFilters | None = ...,
        limiet: int | None = ...,
        met_details: Literal[False] = ...,
    ) -> list[Organisatie]: ...

    @overload
    async def zoek_organisaties(
        self,
        crebocode: int | None = ...,
        *,
        plaats: str | None = ...,
        straal: Straal | int = ...,
        locatie_type: LocatieType | None = ...,
        niveau: Niveau | None = ...,
        organisatie: str | None = ...,
        sortering: Sortering | None = ...,
        alleen_zonder_leerplaatsen: bool = ...,
        buitenland: bool = ...,
        leerweg: Leerweg | None = ...,
        filters: EducatieFilters | None = ...,
        limiet: int | None = ...,
        met_details: Literal[True] = ...,
    ) -> list[OrganisationDetail]: ...

    async def zoek_organisaties(
        self,
        crebocode: int | None = None,
        *,
        plaats: str | None = None,
        straal: Straal | int = Straal.KM_25,
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
        """Zoek naar (erkende) leerbedrijven.

        Parameters
        ----------
        crebocode: int | None
            De CREBO code van de opleiding. Standaard ``None`` voor alle leerbedrijven.
        plaats: str | None
            De plaats/stad of postcode waar gezocht moet worden (bijv. "Amsterdam"). Standaard op ``None`` voor
            landelijke zoekopdracht.
        straal: Straal | int
            De zoekradius in kilometers (standaard: 25km). Dit kan een Straal enum zijn of een integer waarde.
        locatie_type: LocatieType | None
            Soort zoekgebied van ``plaats`` (plaats of postcode). Standaard ``None``.
        niveau: Niveau | None
            Het onderwijsniveau. Standaard ``None``.
        organisatie: str | None
            (Deel van) de naam van het bedrijf. Zie ook :meth:`zoek_organisatienamen`.
        sortering: Sortering | None
            Sorteervolgorde van de resultaten. Standaard ``None`` (relevantie).
        alleen_zonder_leerplaatsen: bool
            Alleen erkende leerbedrijven zonder open leerplaatsen, zoals de website toont
            onder "Erkende bedrijven met mogelijk een plek" (standaard: False).
        buitenland: bool
            Alleen buitenlandse leerbedrijven (standaard: False).
        leerweg: Leerweg | None
            Wordt door de API genegeerd voor organisaties; alleen behouden voor compatibiliteit.
        filters: EducatieFilters | None
            Aanvullende filters, zoals bedrijfssoort, bedrijfsgrootte, sector en land.
        limiet: int | None
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
            locatie_type=locatie_type,
            niveau=niveau,
            organisatie=organisatie,
            sortering=sortering,
            alleen_zonder_leerplaatsen=alleen_zonder_leerplaatsen,
            buitenland=buitenland,
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

    async def zoek_locaties(
        self,
        term: str | None = None,
        *,
        lat: float | None = None,
        lon: float | None = None,
    ) -> LocatieSuggestie:
        """Zoek naar locatie suggesties.

        Parameters
        ----------
        term: str | None
            De zoekterm (bijv. plaatsnaam, postcode of regio).

            Het is de bedoeling om suggesties te krijgen voor locaties die overeenkomen met de opgegeven term.
        lat: float | None
            Breedtegraad. Samen met ``lon`` wordt de dichtstbijzijnde plaats teruggegeven.
        lon: float | None
            Lengtegraad. Samen met ``lat`` wordt de dichtstbijzijnde plaats teruggegeven.

        Returns
        -------
        LocatieSuggestie
            Locatie suggesties die match met de zoekterm.
        """
        return await self.__http.haal_locaties(term=term, lat=lat, lon=lon)

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

    async def zoek_organisatienamen(self, term: str) -> list[str]:
        """Zoek organisatienamen voor autocomplete.

        Parameters
        ----------
        term: str
            (Deel van) de naam van de organisatie, minimaal 2 tekens.

        Returns
        -------
        list[str]
            Gevonden namen; te gebruiken als ``organisatie`` in :meth:`zoek_organisaties`.
        """
        return await self.__http.zoek_organisatienamen(term=term)

    async def haal_regios(self) -> list[RegioInfo]:
        """Haal alle regio's op.

        Returns
        -------
        list[RegioInfo]
            Alle regio's zoals de API ze nu teruggeeft. Voor ``regio`` in :meth:`zoek_stages`
            kun je ook direct de enum :class:`Regio` gebruiken.
        """
        return await self.__http.haal_regios()

    async def haal_filter_opties(
        self,
        *,
        organisaties: bool = False,
        crebocode: int | None = None,
        niveau: Niveau | None = None,
        plaats: str | None = None,
        straal: Straal | int | None = None,
        locatie_type: LocatieType | None = None,
        regio: Regio | str | None = None,
        filters: EducatieFilters | None = None,
    ) -> list[ZoekFilter]:
        """Haal alle filteropties (met aantal resultaten) op voor een zoekopdracht.

        Hiermee krijg je o.a. alle bedrijfssoorten, bedrijfsgroottes, sectoren,
        landen, leerwegen, kenmerken en vergoedingen die bij een zoekopdracht horen,
        zoals het filtermenu op stagemarkt.nl.

        Parameters
        ----------
        organisaties: bool
            ``True`` voor de filters van leerbedrijven, ``False`` (standaard) voor die van stages.
        crebocode: int | None
            De CREBO code van de opleiding.
        niveau: Niveau | None
            Het onderwijsniveau.
        plaats: str | None
            Plaats of postcode. ``None`` voor heel Nederland.
        straal: Straal | int | None
            Zoekradius in kilometers. Standaard 15km wanneer een plaats is opgegeven.
        locatie_type: LocatieType | None
            Soort zoekgebied.
        regio: Regio | str | None
            De regio of het ID ervan (alleen voor stages).
        filters: EducatieFilters | None
            Filters die al toegepast moeten worden.

        Returns
        -------
        list[ZoekFilter]
            Filters met hun opties; :attr:`ZoekFilter.id` is de naam van de query parameter.
        """
        return await self.__http.haal_filter_opties(
            organisaties=organisaties,
            crebocode=crebocode,
            niveau=niveau,
            plaats_postcode=plaats,
            straal=straal,
            locatie_type=locatie_type,
            regio=regio,
            filters=filters,
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

    async def haal_filter_definities(self) -> list[FilterDefinitie]:
        """Haal de filterdefinities op zoals ingesteld in het CMS van stagemarkt.nl.

        Returns
        -------
        list[FilterDefinitie]
            Alle filters met parameternaam, label, type en vaste opties (bijv. straal en niveau).
        """
        return await self.__http.haal_filter_definities()

    async def haal_pagina(self, route: str) -> dict[str, Any]:
        """Haal de ruwe CMS-inhoud van een pagina van stagemarkt.nl op.

        Parameters
        ----------
        route: str
            Pad van de pagina, bijv. ``"/stages"`` of ``"/leerbedrijven"``.

        Returns
        -------
        dict[str, Any]
            De ruwe inhoud; zoekpagina's bevatten o.a. de filters en sorteeropties.
        """
        return await self.__http.haal_pagina(route=route)

    async def haal_vertalingen(self) -> dict[str, dict[str, str]]:
        """Haal alle teksten van de website op, per categorie.

        Returns
        -------
        dict[str, dict[str, str]]
            Per categorie een mapping van naam naar tekst.
        """
        return await self.__http.haal_vertalingen()

    async def haal_formulier(self, formulier: FormulierSoort | str) -> Formulier:
        """Haal de definitie (velden) van een formulier op.

        Parameters
        ----------
        formulier: FormulierSoort | str
            Het formulier, bijv. `FormulierSoort.SOLLICITATIE`, of het ID ervan.

        Returns
        -------
        Formulier
            Het formulier met zijn velden.
        """
        return await self.__http.haal_formulier(formulier=formulier)

    async def haal_stage_preview(self, token: str) -> StagePreview | None:
        """Haal een voorbeeldweergave van een (nog niet gepubliceerde) stage op.

        Parameters
        ----------
        token: str
            Het preview-token uit ``https://stagemarkt.nl/stages/preview?token=...``.

        Returns
        -------
        StagePreview | None
            De stage, of ``None`` als het token ongeldig is.
        """
        return await self.__http.haal_stage_preview(token=token)

    async def haal_mail_alert(self, mail_guid: str) -> MailAlert:
        """Haal een mail alert en de opgeslagen zoekopdrachten op.

        Parameters
        ----------
        mail_guid: str
            De ``mailGuid`` uit de link in een mail alert e-mail.

        Returns
        -------
        MailAlert
            De mail alert.
        """
        return await self.__http.haal_mail_alert(mail_guid=mail_guid)

    async def maak_mail_alert(
        self,
        *,
        email: str,
        zoekopdrachten: list[MailAlertItem],
        toestemming: bool,
        nieuwsbrief: bool = False,
    ) -> dict[str, Any]:
        """Maak een mail alert aan; je krijgt dan een e-mail bij nieuwe stages.

        Parameters
        ----------
        email: str
            E-mailadres voor de meldingen.
        zoekopdrachten: list[MailAlertItem]
            Zoekopdrachten om op te slaan, zie :meth:`MailAlertItem.van_locatie`.
        toestemming: bool
            Akkoord met de privacyverklaring van SBB; moet ``True`` zijn.
        nieuwsbrief: bool
            Ook inschrijven voor de nieuwsbrief (standaard: False).

        Returns
        -------
        dict[str, Any]
            Het antwoord van de server.
        """
        return await self.__http.maak_mail_alert(
            email=email,
            zoekopdrachten=zoekopdrachten,
            toestemming=toestemming,
            nieuwsbrief=nieuwsbrief,
        )

    async def wijzig_mail_alert(
        self,
        mail_guid: str,
        *,
        verwijder: list[MailAlertItem] | None = None,
        nieuwsbrief: bool | None = None,
    ) -> dict[str, Any]:
        """Verwijder zoekopdrachten uit een mail alert en/of wijzig de nieuwsbriefinschrijving.

        Parameters
        ----------
        mail_guid: str
            De ``mailGuid`` uit de link in een mail alert e-mail.
        verwijder: list[MailAlertItem] | None
            Zoekopdrachten om te verwijderen, uit :attr:`MailAlert.items`.
        nieuwsbrief: bool | None
            Nieuwe nieuwsbriefinschrijving; ``None`` laat deze ongewijzigd.

        Returns
        -------
        dict[str, Any]
            Het antwoord van de server.
        """
        return await self.__http.wijzig_mail_alert(mail_guid=mail_guid, verwijder=verwijder, nieuwsbrief=nieuwsbrief)

    async def solliciteer(
        self,
        leerplaats_id: str,
        *,
        naam: str,
        email: str,
        telefoonnummer: str,
        motivatie: str,
        toestemming: bool,
        online_cv: str | None = None,
        bestanden: list[str | Path] | None = None,
    ) -> dict[str, Any]:
        """Solliciteer op een stage. Dit stuurt echt een sollicitatie naar het leerbedrijf.

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
            Akkoord met de privacyverklaring van SBB; moet ``True`` zijn.
        online_cv: str | None
            Link naar een online CV.
        bestanden: list[str | Path] | None
            CV en/of motivatiebrief (.pdf, .docx, .doc of .txt, max. 5 MB per bestand).

        Returns
        -------
        dict[str, Any]
            Het antwoord van de server.
        """
        return await self.__http.solliciteer(
            leerplaats_id=leerplaats_id,
            naam=naam,
            email=email,
            telefoonnummer=telefoonnummer,
            motivatie=motivatie,
            toestemming=toestemming,
            online_cv=online_cv,
            bestanden=bestanden,
        )

    async def stel_vraag_over_stage(
        self,
        leerplaats_id: str,
        *,
        naam: str,
        email: str,
        telefoonnummer: str,
        vraag: str,
        toestemming: bool,
    ) -> dict[str, Any]:
        """Stel een vraag over een stage. Dit stuurt echt een e-mail naar het leerbedrijf.

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
            Akkoord met de privacyverklaring van SBB; moet ``True`` zijn.

        Returns
        -------
        dict[str, Any]
            Het antwoord van de server.
        """
        return await self.__http.stel_vraag_over_stage(
            leerplaats_id=leerplaats_id,
            naam=naam,
            email=email,
            telefoonnummer=telefoonnummer,
            vraag=vraag,
            toestemming=toestemming,
        )

    async def stel_vraag_aan_leerbedrijf(
        self,
        organisatie_id: str,
        *,
        naam: str,
        email: str,
        telefoonnummer: str,
        vraag: str,
        toestemming: bool,
    ) -> dict[str, Any]:
        """Stel een vraag aan een leerbedrijf. Dit stuurt echt een e-mail naar het leerbedrijf.

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
            Akkoord met de privacyverklaring van SBB; moet ``True`` zijn.

        Returns
        -------
        dict[str, Any]
            Het antwoord van de server.
        """
        return await self.__http.stel_vraag_aan_leerbedrijf(
            organisatie_id=organisatie_id,
            naam=naam,
            email=email,
            telefoonnummer=telefoonnummer,
            vraag=vraag,
            toestemming=toestemming,
        )

    async def meld_probleem(
        self,
        leerplaats_id: str,
        *,
        toelichting: str,
        naam: str,
        email: str,
        toestemming: bool,
        soort: ProbleemSoort | None = None,
    ) -> dict[str, Any]:
        """Meld dat er iets niet klopt aan een stage ("Klopt iets niet?").

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
            Akkoord met de privacyverklaring van SBB; moet ``True`` zijn.
        soort: ProbleemSoort | None
            Wat er niet klopt, bijv. `ProbleemSoort.STAGE_VERVULD`.

        Returns
        -------
        dict[str, Any]
            Het antwoord van de server.
        """
        return await self.__http.meld_probleem(
            leerplaats_id=leerplaats_id,
            toelichting=toelichting,
            naam=naam,
            email=email,
            toestemming=toestemming,
            soort=soort,
        )
