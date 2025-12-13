from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from internals._types.adres import (
        AdresCoordinaten,
        AdresLand,
        BaseAdres as AdresPayload,
    )


__all__ = ("Adres", "Land")


class Land:
    """Representatie van een adres land uit de Stagemarkt API.

    Attributes
    ----------
    code: str
        Landcode (bijv. "NL" voor Nederland).
    id: str
        Unieke land-ID.
    naam: str
        Naam van het land (bijv. "Nederland").
    """

    __slots__ = ("code", "id", "naam")

    def __init__(self, data: AdresLand) -> None:
        self.code: str = data.get("code", "")
        self.naam: str = data.get("naam", data.get("name", ""))
        self.id: str = data.get("id", "")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} code={self.code!r} naam={self.naam!r}>"


class Adres:
    """Representatie van een adres uit de Stagemarkt API.

    Attributes
    ----------
    straat: str
        Straatnaam van het adres.
    huisnummer: str
        Huisnummer van het adres.
    postcode: str
        Postcode van het adres.
    plaats: str
        Plaatsnaam van het adres.
    locatie_plaats: str | None
        Locatieplaats van het adres, indien aanwezig.
    lat: float | None
        Latitude van het adres, indien aanwezig.
    lon: float | None
        Longitude van het adres, indien aanwezig.
    land: Land | None
        Land van het adres, indien aanwezig.
    """

    __slots__ = (
        "huisnummer",
        "land",
        "lat",
        "locatie_plaats",
        "lon",
        "plaats",
        "postcode",
        "straat",
    )

    def __init__(
        self,
        *,
        straat: str,
        huisnummer: str,
        postcode: str,
        plaats: str,
        locatie_plaats: str | None = None,
        coordinaten: AdresCoordinaten | None = None,
        land: AdresLand | None = None,
    ) -> None:
        self.straat: str = straat
        self.huisnummer: str = huisnummer
        self.postcode: str = postcode
        self.plaats: str = plaats
        self.locatie_plaats: str | None = locatie_plaats

        self.lat: float | None = coordinaten.get("lat") if coordinaten else None
        self.lon: float | None = coordinaten.get("lon") if coordinaten else None
        self.land: Land | None = Land(land) if land else None

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} straat={self.straat!r} huisnummer={self.huisnummer!r} "
            f"postcode={self.postcode!r} plaats={self.plaats!r}>"
        )

    @classmethod
    def from_dict(cls, data: AdresPayload) -> Adres:
        """Maak een ``Adres`` vanuit een ruwe dictionary.

        Parameters
        ----------
        data: AdresPayload
            Ruwe adrespayload zoals deze uit de API komt.

        Returns
        -------
        Adres
            De gemaakte adresinstantie.
        """

        return cls(
            straat=data.get("straat", ""),
            huisnummer=data.get("huisnummer", ""),
            postcode=data.get("postcode", ""),
            plaats=data.get("plaats", ""),
            locatie_plaats=data.get("locatiePlaats"),
            coordinaten=data.get("coordinaten"),
            land=data.get("land"),
        )
