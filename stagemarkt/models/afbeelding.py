from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from internals._types.afbeelding import Afbeelding as AfbeeldingPayload


__all__ = ("Afbeelding",)


class Afbeelding:
    """Representatie van een afbeelding uit de Stagemarkt API.

    Attributes
    ----------
    opslag_id: str
        Unieke opslag-ID van de afbeelding.
    url: str
        URL naar de afbeelding.
    volgnummer: int
        Volgnummer van de afbeelding.
    """

    __slots__ = ("opslag_id", "url", "volgnummer")

    def __init__(self, data: AfbeeldingPayload) -> None:
        self.opslag_id: str = data["opslagId"]
        self.volgnummer: int = data["volgnummer"]
        self.url: str = data["url"]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} opslag_id={self.opslag_id!r} volgnummer={self.volgnummer} url={self.url!r}>"
