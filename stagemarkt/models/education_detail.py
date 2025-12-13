"""Detailmodel voor een leerplaats.

``EducationDetail`` is een uitbreiding op ``Educatie`` met extra velden die
alleen beschikbaar zijn in de detail-endpoint payload.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .educatie import Educatie
from .kerntaak import Kerntaak

if TYPE_CHECKING:
    from internals._types.educatie_detail import (
        EducationDetail as EducationDetailPayload,
    )

__all__ = ("EducationDetail",)


class EducationDetail(Educatie):
    """
    Representatie van een stage/leerplaats uit de Stagemarkt API maar dan met meer details
    zoals het contactpersoon, aantal beschikbare plekken, etc.

    Attributes
    ----------
    aanbieden: str
        Informatie over wat er wordt aangeboden in de leerplaats.
    aantal: int
        Aantal beschikbare plekken.
    contactpersoon: str
        Naam van de contactpersoon.
    emailadres: str
        E-mailadres van de contactpersoon.
    id: str
        Unieke ID van de leerplaats.
    media: list[str]
        Lijst met mediabestanden (URL's) die bij de leerplaats horen.
    omschrijving: str
        Omschrijving van de leerplaats.
    telefoon: str
        Telefoonnummer van de contactpersoon.
    vaardigheden: str
        Beschrijving van de vaardigheden die worden geleerd in de leerplaats.
    website: str
        Website van de leerplaats.
    kerntaken: list[Kerntaak]
        Lijst met kerntaken die bij de leerplaats horen.
    """

    __slots__ = (
        "_kerntaken",
        "aanbieden",
        "aantal",
        "contactpersoon",
        "emailadres",
        "id",
        "media",
        "omschrijving",
        "telefoon",
        "vaardigheden",
        "website",
    )

    def __init__(self, data: EducationDetailPayload) -> None:
        super().__init__(data)  # pyright: ignore[reportArgumentType]
        # extra fields present on the detail payload
        self.aantal: int = data.get("aantal", 0)
        self.contactpersoon: str = data.get("contactpersoon", "")
        self.emailadres: str = data.get("emailadres", "")
        self.telefoon: str = data.get("telefoon", "")
        # `Educatie` has `leerplaats_id` and other fields; keep `id` too
        self.id: str = data.get("id", "")
        self.omschrijving: str = data.get("omschrijving", "")
        self.vaardigheden: str = data.get("vaardigheden", "")
        self.aanbieden: str = data.get("aanbieden", "")
        self.website: str = data.get("website", "")

        # kerntaken and media are specific to the detail payload
        self._kerntaken = data.get("kerntaken", [])
        self.media: list[str] = data.get("media", [])

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id!r} title={self.title!r}>"

    @property
    def kerntaken(self) -> list[Kerntaak]:
        """list[:class:`Kerntaak`]: lijst met kerntaken die bij de leerplaats horen."""
        return [Kerntaak(k) for k in getattr(self, "_kerntaken", [])]
