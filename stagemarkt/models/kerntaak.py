"""Modellen voor kerntaken en subtaken."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from internals._types.educatie_detail import (
        EducationDetailKerntaak as EducationDetailKerntaakPayload,
        EducationDetailKerntaakSubtaak as EducationDetailKerntaakSubtaakPayload,
    )
    from internals._types.organisation_detail import (
        Kerntaak as OrganisationDetailKerntaakPayload,
        KerntaakSubtaak as OrganisationDetailKerntaakSubtaakPayload,
    )


__all__ = ("Kerntaak", "KerntaakSubtaak")


class KerntaakSubtaak:
    """Representatie van een kerntaak's subtaak.

    Attributes
    ----------
    code: str
        Code van de subtaak.
    id: str
        Unieke ID van de subtaak.
    naam: str
        Naam van de subtaak.
    uitvoerbaar: bool
        ``True`` indien de subtaak uitvoerbaar is, anders ``False``.
    """

    __slots__ = ("code", "id", "naam", "uitvoerbaar")

    def __init__(
        self,
        data: EducationDetailKerntaakSubtaakPayload | OrganisationDetailKerntaakSubtaakPayload,
    ) -> None:
        self.id: str = data.get("id", "")
        self.code: str = data.get("code", "")
        self.naam: str = data.get("naam", "")
        self.uitvoerbaar: bool = data.get("uitvoerbaar", False)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} code={self.code!r} naam={self.naam!r}>"


class Kerntaak:
    """Representatie van een kerntaak.

    Attributes
    ----------
    subtaken: list[:class:`KerntaakSubtaak`]
        Subtaken behorend bij de kerntaak.
    aantal_subtaken: int
        Totaal aantal subtaken.
    aantal_uitvoerbaar: int
        Aantal uitvoerbare subtaken.
    code: str
        Code van de kerntaak.
    id: str
        Unieke ID van de kerntaak.
    naam: str
        Naam van de kerntaak.
    """

    __slots__ = ("_subtaken", "aantal_subtaken", "aantal_uitvoerbaar", "code", "id", "naam")

    def __init__(
        self,
        data: EducationDetailKerntaakPayload | OrganisationDetailKerntaakPayload,
    ) -> None:
        self.id: str = data.get("id", "")
        self.code: str = data.get("code", "")
        self.naam: str = data.get("naam", "")
        self.aantal_subtaken: int = data.get("aantalSubtaken", 0)
        self.aantal_uitvoerbaar: int = data.get("aantalUitvoerbaar", 0)
        self._subtaken = data.get("subtaken", [])

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} code={self.code!r} naam={self.naam!r}>"

    @property
    def subtaken(self) -> list[KerntaakSubtaak]:
        """list[:class:`KerntaakSubtaak`]: subtaken behorend bij de kerntaak."""

        return [KerntaakSubtaak(s) for s in self._subtaken]
