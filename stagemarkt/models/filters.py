"""Filtermodel voor het samenstellen van zoekparameters.

Deze module bevat ``EducatieFilters``: een kleine helper om filters te
combineren en om te zetten naar query parameters of weer terug te lezen uit een
URL.
"""

from __future__ import annotations

from typing import Any, Self
from collections.abc import Sequence
from enum import Enum
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

from ..enums import Leerweg, Sector, SoortBedrijf

__all__ = ("EducatieFilters",)


class EducatieFilters:
    """Filters voor het zoeken naar leerplaatsen.

    Parameters
    ----------
    bedrijf_soorten: list[SoortBedrijf | str] | None
        Eén of meerdere bedrijfstypen (enum of ruwe string-waarde).
    sectoren: list[Sector | str] | None
        Eén of meerdere sectoren (enum of ruwe string-waarde).
    leerwegen: list[Leerweg | str] | None
        Eén of meerdere leerwegen (enum of ruwe string-waarde).
    trefwoorden: Sequence[str] | None
        Eén of meerdere trefwoorden; een string wordt als enkel item behandeld.
    """

    __slots__ = ("bedrijf_soorten", "leerwegen", "sectoren", "trefwoorden")

    def __init__(
        self,
        bedrijf_soorten: list[SoortBedrijf | str] | None = None,
        sectoren: list[Sector | str] | None = None,
        leerwegen: list[Leerweg | str] | None = None,
        trefwoorden: Sequence[str] | None = None,
    ) -> None:
        self.bedrijf_soorten: list[SoortBedrijf | str] = bedrijf_soorten or []
        self.sectoren: list[Sector | str] = sectoren or []
        self.leerwegen: list[Leerweg | str] = leerwegen or []

        if trefwoorden is None:
            self.trefwoorden: list[str] = []
        elif isinstance(trefwoorden, str):
            self.trefwoorden: list[str] = [trefwoorden]
        else:
            self.trefwoorden: list[str] = list(trefwoorden)

    def merge(self, other: EducatieFilters) -> None:
        """Voeg ontbrekende filterwaarden toe vanuit een andere instantie.

        Parameters
        ----------
        other: EducatieFilters
            Filters die gemerged worden in de huidige instantie.
        """

        self.bedrijf_soorten.extend(bs for bs in other.bedrijf_soorten if bs not in self.bedrijf_soorten)
        self.sectoren.extend(s for s in other.sectoren if s not in self.sectoren)
        self.leerwegen.extend(lw for lw in other.leerwegen if lw not in self.leerwegen)
        self.trefwoorden.extend(kw for kw in other.trefwoorden if kw not in self.trefwoorden)

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

    @classmethod
    def from_url(cls, url: str) -> Self:
        """Maak filters op basis van een URL met querystring.

        Parameters
        ----------
        url : str
            URL met query parameters zoals die door de API gebruikt worden.

        Returns
        -------
        Self
            Nieuwe filterinstantie.
        """

        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        bedrijf_soorten: Sequence[SoortBedrijf | str] = params.get("companyType", [])
        sectoren: Sequence[Sector | str] = params.get("sector", [])
        leerwegen: Sequence[Leerweg | str] = params.get("learningPath", [])
        trefwoorden: list[str] = [unquote(k) for k in params.get("keyword", [])]

        # Try to convert to enum if possible, otherwise keep as string
        def try_enum[EnumT: Enum](enum_cls: type[EnumT], value: str) -> EnumT | str:
            try:
                return enum_cls(value)
            except Exception:  # noqa: BLE001
                return value

        bedrijf_soorten = [try_enum(SoortBedrijf, unquote(b)) for b in bedrijf_soorten]
        sectoren = [try_enum(Sector, unquote(s)) for s in sectoren]
        leerwegen = [try_enum(Leerweg, unquote(le)) for le in leerwegen]

        return cls(
            bedrijf_soorten=bedrijf_soorten,
            sectoren=sectoren,
            leerwegen=leerwegen,
            trefwoorden=trefwoorden,
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
        if self.bedrijf_soorten:
            params.extend(("companyType", bs.value if isinstance(bs, SoortBedrijf) else bs) for bs in self.bedrijf_soorten)
        if self.sectoren:
            params.extend(("sector", s.value if isinstance(s, Sector) else s) for s in self.sectoren)
        if self.leerwegen:
            params.extend(("learningPath", lw.value if isinstance(lw, Leerweg) else lw) for lw in self.leerwegen)
        if self.trefwoorden:
            params.append(
                ("keyword", "+".join(quote_plus(kw) for kw in self.trefwoorden))
                if not isinstance(self.trefwoorden, str)
                else ("keyword", self.trefwoorden),
            )
        return params

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} bedrijf_soorten={len(self.bedrijf_soorten)} "
            f"sectoren={len(self.sectoren)} leerwegen={len(self.leerwegen)} "
            f"trefwoorden={self.trefwoorden!r}>"
        )
