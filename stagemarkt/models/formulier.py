"""Modellen voor formulieren, mail alerts en stage previews.

Stagemarkt gebruikt Umbraco Forms voor sollicitaties, vragen aan leerbedrijven,
het melden van fouten en mail alerts. ``Formulier`` beschrijft de velden van
zo'n formulier; ``MailAlert`` en ``MailAlertItem`` beschrijven opgeslagen
zoekopdrachten.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self
from enum import Enum
import datetime

from ..enums import FilterType, FormulierVeldType, Leerweg, Straal

if TYPE_CHECKING:
    from internals._types.formulier import (
        FilterDefinitie as FilterDefinitiePayload,
        Formulier as FormulierPayload,
        FormulierVeld as FormulierVeldPayload,
        MailAlert as MailAlertPayload,
        MailAlertItem as MailAlertItemPayload,
    )

    from .locatie import Locatie

__all__ = (
    "FilterDefinitie",
    "Formulier",
    "FormulierVeld",
    "MailAlert",
    "MailAlertItem",
    "StagePreview",
)


def _als_enum[EnumT: Enum](enum_cls: type[EnumT], waarde: str) -> EnumT | str:
    try:
        return enum_cls(waarde)
    except ValueError:
        return waarde


class FormulierVeld:
    """Eén veld van een formulier.

    Attributes
    ----------
    alias: str
        Naam van het veld zoals die bij het versturen gebruikt wordt.
    label: str
        Leesbaar label van het veld.
    type: FormulierVeldType | str
        Soort veld, bijv. `FormulierVeldType.BESTAND`. Onbekende soorten blijven een string.
    verplicht: bool
        Of het veld verplicht is.
    opties: list[str]
        Mogelijke waarden bij keuzevelden.
    """

    __slots__ = ("alias", "label", "opties", "type", "verplicht")

    def __init__(self, data: FormulierVeldPayload) -> None:
        self.alias: str = data.get("alias", "")
        self.label: str = data.get("caption", "")
        soort = (data.get("type") or {}).get("name", "").strip()
        self.type: FormulierVeldType | str = _als_enum(FormulierVeldType, soort)
        self.verplicht: bool = data.get("required", False)
        self.opties: list[str] = [o.get("value", "") for o in data.get("preValues") or []]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} alias={self.alias!r} type={self.type!r} verplicht={self.verplicht}>"


class Formulier:
    """Definitie van een (Umbraco) formulier.

    Attributes
    ----------
    id: str
        ID van het formulier.
    naam: str
        Naam van het formulier.
    velden: list[FormulierVeld]
        Alle velden van het formulier, in volgorde.
    """

    __slots__ = ("id", "naam", "velden")

    def __init__(self, data: FormulierPayload) -> None:
        self.id: str = data.get("id", "")
        self.naam: str = data.get("name", "")
        self.velden: list[FormulierVeld] = [
            FormulierVeld(veld)
            for pagina in data.get("pages") or []
            for fieldset in pagina.get("fieldsets") or []
            for kolom in fieldset.get("columns") or []
            for veld in kolom.get("fields") or []
        ]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} naam={self.naam!r} velden={len(self.velden)}>"


class MailAlertItem:
    """Een opgeslagen zoekopdracht binnen een mail alert.

    Parameters
    ----------
    crebocode: int | None
        CREBO-code van de opleiding.
    postcode: str | None
        Postcode (of plaatsnaam) van het zoekgebied.
    latitude: float | None
        Breedtegraad van het zoekgebied.
    longitude: float | None
        Lengtegraad van het zoekgebied.
    straal: Straal | int | None
        Zoekstraal in kilometers.
    label: str
        Omschrijving van de zoekopdracht, bijv. ``"Software developer in Amsterdam"``.
    """

    __slots__ = ("crebocode", "label", "latitude", "longitude", "postcode", "site_type", "straal")

    def __init__(
        self,
        *,
        crebocode: int | None = None,
        postcode: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        straal: Straal | int | None = None,
        label: str = "Zoekopdracht",
        site_type: str = "2",
    ) -> None:
        self.crebocode: int | None = crebocode
        self.postcode: str | None = postcode
        self.latitude: float | None = latitude
        self.longitude: float | None = longitude
        self.straal: int | None = straal.value if isinstance(straal, Straal) else straal
        self.label: str = label
        self.site_type: str = site_type

    @classmethod
    def van_locatie(
        cls,
        locatie: Locatie,
        *,
        crebocode: int | None = None,
        straal: Straal | int | None = None,
        label: str = "Zoekopdracht",
    ) -> Self:
        """Maak een item op basis van een locatie-suggestie (zie ``StagemarktClient.zoek_locaties``)."""
        plaats = locatie.plaats
        return cls(
            crebocode=crebocode,
            postcode=(plaats.postcode or plaats.naam) if plaats else locatie.suggestie,
            latitude=plaats.lat if plaats else None,
            longitude=plaats.lon if plaats else None,
            straal=straal,
            label=label,
        )

    @classmethod
    def from_payload(cls, data: MailAlertItemPayload) -> Self:
        def num(value: Any, cast: type[int | float]) -> Any:
            try:
                return cast(value) if value not in (None, "") else None
            except (TypeError, ValueError):
                return None

        return cls(
            crebocode=num(data.get("crebocode"), int),
            postcode=data.get("postcode"),
            latitude=num(data.get("latitude"), float),
            longitude=num(data.get("longitude"), float),
            straal=num(data.get("range"), int),
            label=data.get("label", ""),
            site_type=data.get("siteType", "2"),
        )

    def to_payload(self) -> MailAlertItemPayload:
        """Zet het item om naar het formaat dat de website verstuurt (alle waarden als string)."""

        def text(value: object) -> str | None:
            return None if value is None else str(value)

        return {
            "siteType": self.site_type,
            "postcode": text(self.postcode),
            "latitude": text(self.latitude),
            "longitude": text(self.longitude),
            "range": text(self.straal),
            "crebocode": text(self.crebocode),
            "label": self.label,
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} label={self.label!r} crebocode={self.crebocode} postcode={self.postcode!r}>"


class MailAlert:
    """Een mail alert met opgeslagen zoekopdrachten.

    Attributes
    ----------
    email: str
        E-mailadres van de mail alert.
    nieuwsbrief: bool
        Of het e-mailadres ook is ingeschreven voor de nieuwsbrief.
    items: list[MailAlertItem]
        Opgeslagen zoekopdrachten.
    """

    __slots__ = ("email", "items", "nieuwsbrief")

    def __init__(self, data: MailAlertPayload) -> None:
        self.email: str = data.get("email", "")
        self.nieuwsbrief: bool = bool(data.get("isNewsletterSubscribed", False))
        self.items: list[MailAlertItem] = [MailAlertItem.from_payload(i) for i in data.get("items") or []]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} email={self.email!r} items={len(self.items)}>"


class FilterDefinitie:
    """Definitie van een zoekfilter zoals ingesteld in het CMS van stagemarkt.nl.

    Attributes
    ----------
    naam: str
        Naam van de query parameter, bijv. ``"straal"``.
    label: str
        Label op de website.
    type: FilterType | str
        Soort filter, bijv. `FilterType.VAST`. Onbekende soorten blijven een string.
    opties: dict[str, str]
        Vaste opties (waarde -> label); leeg bij dynamische filters, zie
        ``StagemarktClient.haal_filter_opties`` voor die opties.
    standaard: str | None
        Standaardwaarde, indien aanwezig.
    """

    __slots__ = ("label", "naam", "opties", "standaard", "type")

    def __init__(self, data: FilterDefinitiePayload) -> None:
        self.naam: str = data.get("filterName", "")
        self.label: str = data.get("label", "")
        self.type: FilterType | str = _als_enum(FilterType, data.get("__filtertype", ""))
        opties = data.get("options") or []
        self.opties: dict[str, str] = {o.get("value", ""): o.get("label", "") for o in opties}
        self.standaard: str | None = next((o.get("value") for o in opties if o.get("default")), None)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} naam={self.naam!r} type={self.type!r} opties={len(self.opties)}>"


class StagePreview:
    """Voorbeeldweergave van een (nog niet gepubliceerde) stage, op te halen met een preview-token.

    Attributes
    ----------
    titel: str | None
        Wervende titel van de stage.
    kwalificatie: str | None
        Naam van de kwalificatie (opleiding).
    crebocode: str | None
        CREBO-code van de kwalificatie.
    niveau: int | None
        Niveau van de kwalificatie.
    organisatie: str | None
        Naam van de organisatie.
    leerweg: Leerweg | None
        BOL of BBL.
    contactpersoon: str | None
        Naam van de contactpersoon.
    emailadres: str | None
        E-mailadres voor de stage.
    telefoon: str | None
        Telefoonnummer voor de stage.
    omschrijving: str | None
        Omschrijving van de stage.
    aanbieden: str | None
        Wat het leerbedrijf aanbiedt.
    vaardigheden: str | None
        Gevraagde vaardigheden.
    website: str | None
        Website.
    dagen_per_week: int | None
        Aantal dagen per week.
    vergoedingen: list[str]
        Omschrijvingen van de vergoedingen.
    plaats: str | None
        Plaats van de stage.
    """

    __slots__ = (
        "_einddatum",
        "_startdatum",
        "aanbieden",
        "contactpersoon",
        "crebocode",
        "dagen_per_week",
        "emailadres",
        "kwalificatie",
        "leerweg",
        "niveau",
        "omschrijving",
        "organisatie",
        "plaats",
        "telefoon",
        "titel",
        "vaardigheden",
        "vergoedingen",
        "website",
    )

    def __init__(self, data: dict[str, Any]) -> None:
        kwalificatie: dict[str, Any] = data.get("Kwalificatie") or {}
        organisatie: dict[str, Any] = data.get("Organisatie") or {}
        adres: dict[str, Any] = data.get("Adres") or {}

        self.titel: str | None = data.get("Titel")
        self.kwalificatie: str | None = kwalificatie.get("naam")
        self.crebocode: str | None = kwalificatie.get("crebocode")
        self.niveau: int | None = kwalificatie.get("niveau")
        self.organisatie: str | None = organisatie.get("naam")
        self.leerweg: Leerweg | None = Leerweg(lw) if (lw := data.get("LeerwegId")) in Leerweg._value2member_map_ else None
        self.contactpersoon: str | None = data.get("Contactpersoon")
        self.emailadres: str | None = data.get("Emailadres")
        self.telefoon: str | None = data.get("Telefoon")
        self.omschrijving: str | None = data.get("Omschrijving")
        self.aanbieden: str | None = data.get("Voorwaarden")
        self.vaardigheden: str | None = data.get("Vaardigheden")
        self.website: str | None = data.get("Website")
        dagen = str(data.get("DagenPerWeek"))
        self.dagen_per_week: int | None = int(dagen) if dagen.isdigit() else None
        vergoedingen: list[dict[str, Any]] = data.get("Vergoedingen") or []
        self.vergoedingen: list[str] = [v.get("Omschrijving", "") for v in vergoedingen]
        self.plaats: str | None = adres.get("Plaats")
        self._startdatum: str | None = data.get("Startdatum")
        self._einddatum: str | None = data.get("Einddatum")

    @staticmethod
    def _datum(value: str | None) -> datetime.datetime | None:
        if not value:
            return None
        date_str = value.rstrip("Z")
        try:
            return datetime.datetime.fromisoformat(date_str)
        except ValueError:
            return datetime.datetime.fromisoformat(date_str.split("T")[0])

    @property
    def start_op(self) -> datetime.datetime | None:
        """:class:`datetime.datetime` | ``None``: de startdatum van de stage."""
        return self._datum(self._startdatum)

    @property
    def eindigt_op(self) -> datetime.datetime | None:
        """:class:`datetime.datetime` | ``None``: de einddatum van de stage."""
        return self._datum(self._einddatum)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} titel={self.titel!r} organisatie={self.organisatie!r}>"
