"""Filtermodel voor het samenstellen van zoekparameters.

Deze module bevat ``EducatieFilters``: een kleine helper om filters te
combineren en om te zetten naar query parameters of weer terug te lezen uit een
URL. Daarnaast bevat het ``ZoekFilter`` en ``ZoekFilterOptie``: de filteropties
(met aantallen) die de API bij elke zoekopdracht teruggeeft.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self
from collections.abc import Sequence
from enum import Enum
from urllib.parse import parse_qs, unquote, urlparse

from ..enums import Bedrijfsgrootte, Kenmerk, Land, Leerweg, Sector, SoortBedrijf, StartBinnen, VergoedingSoort

if TYPE_CHECKING:
    from internals._types.filters import (
        Filter as FilterPayload,
        FilterOption as FilterOptionPayload,
    )

__all__ = ("EducatieFilters", "ZoekFilter", "ZoekFilterOptie")


def _waarde(item: Enum | str | int) -> str | int:
    return item.value if isinstance(item, Enum) else item


class EducatieFilters:
    """Filters voor het zoeken naar leerplaatsen en leerbedrijven.

    Niet elk filter werkt op beide zoekopdrachten. Zie de parameters hieronder.

    Parameters
    ----------
    bedrijf_soorten: list[SoortBedrijf | str] | None
        Eén of meerdere bedrijfstypen (enum of ruwe string-waarde). Meerdere
        waarden worden gecombineerd (OF).
    sectoren: list[Sector | str] | None
        Eén of meerdere sectoren (enum of ruwe string-waarde).
        Werkt alleen bij het zoeken naar organisaties.
    leerwegen: list[Leerweg | str] | None
        Leerweg(en) (enum of ruwe string-waarde). De API accepteert maar één
        leerweg; wanneer zowel BOL als BBL opgegeven zijn wordt er niet op
        leerweg gefilterd. Werkt alleen bij het zoeken naar stages.
    trefwoorden: Sequence[str] | None
        Eén of meerdere trefwoorden; een string wordt als enkel item behandeld.
    bedrijfsgroottes: list[Bedrijfsgrootte | str] | None
        Eén of meerdere bedrijfsgroottes (enum of ruwe string-waarde).
    kenmerken: list[Kenmerk | str] | None
        Eén of meerdere kenmerken; alle kenmerken moeten van toepassing zijn (EN).
        Werkt alleen bij het zoeken naar stages.
    vergoedingen: list[VergoedingSoort | str] | None
        Eén of meerdere soorten vergoeding. Werkt alleen bij het zoeken naar stages.
    landen: list[Land | str] | None
        Eén of meerdere landen (enum of landcode, bijv. ``"BE"``).
        Werkt alleen bij het zoeken naar organisaties.
    start_binnen_maanden: StartBinnen | int | None
        Alleen leerplaatsen die binnen dit aantal maanden starten (de website
        biedt 1, 3 en 6 aan). Werkt alleen bij het zoeken naar stages.
    alle_werkprocessen_uitvoerbaar: bool | None
        Filter op of alle werkprocessen bij het bedrijf uitvoerbaar zijn.
        Werkt alleen bij het zoeken naar stages.
    """

    __slots__ = (
        "alle_werkprocessen_uitvoerbaar",
        "bedrijf_soorten",
        "bedrijfsgroottes",
        "kenmerken",
        "landen",
        "leerwegen",
        "sectoren",
        "start_binnen_maanden",
        "trefwoorden",
        "vergoedingen",
    )

    def __init__(
        self,
        bedrijf_soorten: list[SoortBedrijf | str] | None = None,
        sectoren: list[Sector | str] | None = None,
        leerwegen: list[Leerweg | str] | None = None,
        trefwoorden: Sequence[str] | None = None,
        *,
        bedrijfsgroottes: list[Bedrijfsgrootte | str] | None = None,
        kenmerken: list[Kenmerk | str] | None = None,
        vergoedingen: list[VergoedingSoort | str] | None = None,
        landen: list[Land | str] | None = None,
        start_binnen_maanden: StartBinnen | int | None = None,
        alle_werkprocessen_uitvoerbaar: bool | None = None,
    ) -> None:
        self.bedrijf_soorten: list[SoortBedrijf | str] = bedrijf_soorten or []
        self.sectoren: list[Sector | str] = sectoren or []
        self.leerwegen: list[Leerweg | str] = leerwegen or []
        self.bedrijfsgroottes: list[Bedrijfsgrootte | str] = bedrijfsgroottes or []
        self.kenmerken: list[Kenmerk | str] = kenmerken or []
        self.vergoedingen: list[VergoedingSoort | str] = vergoedingen or []
        self.landen: list[Land | str] = landen or []
        self.start_binnen_maanden: StartBinnen | int | None = start_binnen_maanden
        self.alle_werkprocessen_uitvoerbaar: bool | None = alle_werkprocessen_uitvoerbaar

        if trefwoorden is None:
            self.trefwoorden: list[str] = []
        elif isinstance(trefwoorden, str):
            self.trefwoorden: list[str] = [trefwoorden]
        else:
            self.trefwoorden: list[str] = list(trefwoorden)

    def merge(self, other: EducatieFilters) -> None:
        """Voeg ontbrekende filterwaarden toe vanuit een andere instantie.

        Enkelvoudige waarden (``start_binnen_maanden`` en
        ``alle_werkprocessen_uitvoerbaar``) worden alleen overgenomen als ze hier
        nog niet ingesteld zijn.

        Parameters
        ----------
        other: EducatieFilters
            Filters die gemerged worden in de huidige instantie.
        """

        self.bedrijf_soorten.extend(bs for bs in other.bedrijf_soorten if bs not in self.bedrijf_soorten)
        self.sectoren.extend(s for s in other.sectoren if s not in self.sectoren)
        self.leerwegen.extend(lw for lw in other.leerwegen if lw not in self.leerwegen)
        self.trefwoorden.extend(kw for kw in other.trefwoorden if kw not in self.trefwoorden)
        self.bedrijfsgroottes.extend(bg for bg in other.bedrijfsgroottes if bg not in self.bedrijfsgroottes)
        self.kenmerken.extend(km for km in other.kenmerken if km not in self.kenmerken)
        self.vergoedingen.extend(vg for vg in other.vergoedingen if vg not in self.vergoedingen)
        self.landen.extend(ld for ld in other.landen if ld not in self.landen)
        if self.start_binnen_maanden is None:
            self.start_binnen_maanden = other.start_binnen_maanden
        if self.alle_werkprocessen_uitvoerbaar is None:
            self.alle_werkprocessen_uitvoerbaar = other.alle_werkprocessen_uitvoerbaar

    def voeg_bedrijf_soort_toe(self, soort: SoortBedrijf | str) -> None:
        """Voeg een bedrijfstype toe als deze nog niet aanwezig is."""

        if soort not in self.bedrijf_soorten:
            self.bedrijf_soorten.append(soort)

    def voeg_sector_toe(self, sector: Sector | str) -> None:
        """Voeg een sector toe als deze nog niet aanwezig is."""

        if sector not in self.sectoren:
            self.sectoren.append(sector)

    def voeg_leerweg_toe(self, leerweg: Leerweg | str) -> None:
        """Voeg een leerweg toe als deze nog niet aanwezig is."""

        if leerweg not in self.leerwegen:
            self.leerwegen.append(leerweg)

    def voeg_trefwoord_toe(self, trefwoord: str) -> None:
        """Voeg een trefwoord toe als deze nog niet aanwezig is."""

        if trefwoord not in self.trefwoorden:
            self.trefwoorden.append(trefwoord)

    def voeg_bedrijfsgrootte_toe(self, grootte: Bedrijfsgrootte | str) -> None:
        """Voeg een bedrijfsgrootte toe als deze nog niet aanwezig is."""

        if grootte not in self.bedrijfsgroottes:
            self.bedrijfsgroottes.append(grootte)

    def voeg_kenmerk_toe(self, kenmerk: Kenmerk | str) -> None:
        """Voeg een kenmerk toe als deze nog niet aanwezig is."""

        if kenmerk not in self.kenmerken:
            self.kenmerken.append(kenmerk)

    def voeg_vergoeding_toe(self, vergoeding: VergoedingSoort | str) -> None:
        """Voeg een vergoeding toe als deze nog niet aanwezig is."""

        if vergoeding not in self.vergoedingen:
            self.vergoedingen.append(vergoeding)

    def voeg_land_toe(self, land: Land | str) -> None:
        """Voeg een landcode toe als deze nog niet aanwezig is."""

        if land not in self.landen:
            self.landen.append(land)

    @classmethod
    def from_url(cls, url: str) -> Self:
        """Maak filters op basis van een URL met querystring.

        Zowel de huidige parameternamen van stagemarkt.nl (``soortBedrijf``,
        ``sectoren``, ``leerweg``, ``termen``, ...) als de oude namen
        (``companyType``, ``sector``, ``learningPath``, ``keyword``) worden herkend.

        Parameters
        ----------
        url : str
            URL met query parameters zoals die door de website of API gebruikt worden.

        Returns
        -------
        Self
            Nieuwe filterinstantie.
        """

        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        def get(*keys: str) -> list[str]:
            return [unquote(v) for key in keys for v in params.get(key, [])]

        # Try to convert to enum if possible, otherwise keep as string
        def try_enum[EnumT: Enum, V](enum_cls: type[EnumT], value: V) -> EnumT | V:
            try:
                return enum_cls(value)
            except Exception:  # noqa: BLE001
                return value

        trefwoorden = [kw for value in get("termen", "keyword") for kw in value.replace("+", " ").split()]
        start = get("startInMonths")
        werkprocessen = get("alleWerkprocessenUitvoerbaar")

        return cls(
            bedrijf_soorten=[try_enum(SoortBedrijf, b) for b in get("soortBedrijf", "companyType")],
            sectoren=[try_enum(Sector, s) for s in get("sectoren", "sector")],
            leerwegen=[try_enum(Leerweg, le) for le in get("leerweg", "learningPath")],
            trefwoorden=trefwoorden,
            bedrijfsgroottes=[try_enum(Bedrijfsgrootte, bg) for bg in get("bedrijfsgrootte")],
            kenmerken=[try_enum(Kenmerk, km) for km in get("kenmerken")],
            vergoedingen=[try_enum(VergoedingSoort, vg) for vg in get("vergoedingen")],
            landen=[try_enum(Land, ld) for ld in get("land")],
            start_binnen_maanden=try_enum(StartBinnen, int(start[0])) if start and start[0].isdigit() else None,
            alle_werkprocessen_uitvoerbaar=werkprocessen[0].lower() == "true" if werkprocessen else None,
        )

    def to_params(self) -> list[tuple[str, Any]]:
        """Zet de filters om naar query parameters.

        Returns
        -------
        list[tuple[str, Any]]
            Lijst van key/value paren die direct gebruikt kan worden voor een
            HTTP client.
        """

        params: list[tuple[str, Any]] = []
        params.extend(("soortBedrijf", _waarde(bs)) for bs in self.bedrijf_soorten)
        params.extend(("sectoren", _waarde(s)) for s in self.sectoren)
        # De API geeft een 500 bij meerdere leerwegen; beide leerwegen == geen filter
        leerwegen = {_waarde(lw) for lw in self.leerwegen}
        if len(leerwegen) == 1:
            params.append(("leerweg", leerwegen.pop()))
        params.extend(("bedrijfsgrootte", _waarde(bg)) for bg in self.bedrijfsgroottes)
        params.extend(("kenmerken", _waarde(km)) for km in self.kenmerken)
        params.extend(("vergoedingen", _waarde(vg)) for vg in self.vergoedingen)
        params.extend(("land", _waarde(ld)) for ld in self.landen)
        if self.trefwoorden:
            params.append(("termen", " ".join(self.trefwoorden)))
        if self.start_binnen_maanden is not None:
            params.append(("startInMonths", _waarde(self.start_binnen_maanden)))
        if self.alle_werkprocessen_uitvoerbaar is not None:
            params.append(("alleWerkprocessenUitvoerbaar", str(self.alle_werkprocessen_uitvoerbaar).lower()))
        return params

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} bedrijf_soorten={len(self.bedrijf_soorten)} "
            f"sectoren={len(self.sectoren)} leerwegen={len(self.leerwegen)} "
            f"bedrijfsgroottes={len(self.bedrijfsgroottes)} kenmerken={len(self.kenmerken)} "
            f"vergoedingen={len(self.vergoedingen)} landen={self.landen!r} "
            f"trefwoorden={self.trefwoorden!r}>"
        )


class ZoekFilterOptie:
    """Eén optie binnen een filter, zoals teruggegeven door een zoekopdracht.

    Attributes
    ----------
    id: str
        Waarde om mee te filteren (meestal een GUID, soms een code zoals ``"NL"``).
    label: str
        Leesbare naam van de optie.
    aantal: int
        Aantal resultaten voor deze optie binnen de huidige zoekopdracht.
    """

    __slots__ = ("aantal", "id", "label")

    def __init__(self, data: FilterOptionPayload) -> None:
        self.id: str = data.get("id", "")
        self.label: str = data.get("label", "")
        self.aantal: int = data.get("hits", 0)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} label={self.label!r} aantal={self.aantal}>"


class ZoekFilter:
    """Een filter met de beschikbare opties voor een zoekopdracht.

    Attributes
    ----------
    id: str
        Naam van de query parameter, bijv. ``"soortBedrijf"`` of ``"bedrijfsgrootte"``.
    opties: list[ZoekFilterOptie]
        Beschikbare opties met het aantal resultaten per optie.
    """

    __slots__ = ("id", "opties")

    def __init__(self, data: FilterPayload) -> None:
        self.id: str = data.get("id", "")
        self.opties: list[ZoekFilterOptie] = [ZoekFilterOptie(o) for o in data.get("options") or []]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id!r} opties={len(self.opties)}>"
