"""Stagemarkt helper utilities."""

from __future__ import annotations

from urllib.parse import quote_plus, urlencode

__all__ = ("maak_stagemarkt_link",)


def maak_stagemarkt_link(
    *,
    educatie_id: str,
    titel: str,
    niveau: int,
    educatie_type: int,
    straal: int,
    crebocode: int,
    plaats_postcode: str,
) -> str:
    """Maak een Stagemarkt link voor een educatie.

    Parameters
    ----------
    educatie_id: str
        De unieke ID van de educatie/leerplaats.
    titel: str
        De titel van de educatie voor de URL slug.
    niveau: int
        Opleidingsniveau.
    educatie_type: int
        Type educatie.
    straal: int
        Zoekstraal in kilometers.
    crebocode: int
        CREBO-code van de opleiding.
    plaats_postcode: str
        Plaats of postcode.

    Returns
    -------
    str
        Volledige Stagemarkt URL.

    Examples
    --------
    >>> maak_stagemarkt_link(
    ...     educatie_id="abc-123",
    ...     titel="Software Developer",
    ...     niveau=4,
    ...     educatie_type=1,
    ...     straal=25,
    ...     crebocode=25998,
    ...     plaats_postcode="Amsterdam"
    ... )
    'https://stagemarkt.nl/stages/software-developer_abc-123?niveau=4&type=1&range=25&crebocode=25998&plaatsPostcode=Amsterdam'
    """
    titel_slug = titel.lower().replace("/", "-").replace(" ", "-")
    titel_slug = quote_plus(titel_slug)

    base_url = f"https://stagemarkt.nl/stages/{titel_slug}_{educatie_id}"

    params = {
        "niveau": niveau,
        "type": educatie_type,
        "range": straal,
        "crebocode": crebocode,
        "plaatsPostcode": plaats_postcode,
    }

    query_string = urlencode(params)

    return f"{base_url}?{query_string}"
