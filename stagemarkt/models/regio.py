"""Model voor regio's."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..enums import Regio

if TYPE_CHECKING:
    from internals._types.regio import Regio as RegioPayload

__all__ = ("RegioInfo",)


class RegioInfo:
    """Representatie van een regio uit de Stagemarkt API.

    Attributes
    ----------
    id: str
        Unieke ID van de regio. Te gebruiken als ``regio`` bij het zoeken naar stages.
    naam: str
        Naam van de regio, bijv. ``"Groot Amsterdam"``.
    """

    __slots__ = ("id", "naam")

    def __init__(self, data: RegioPayload) -> None:
        self.id: str = data.get("id", "")
        self.naam: str = data.get("naam", "")

    @property
    def regio(self) -> Regio | None:
        """:class:`Regio` | ``None``: de bijbehorende enum-waarde, of ``None`` als de regio nieuw is."""
        try:
            return Regio(self.id)
        except ValueError:
            return None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} naam={self.naam!r} id={self.id!r}>"
