from __future__ import annotations

from typing import Any, TypedDict


class FormulierVeldType(TypedDict):
    id: str
    name: str  # bijv. "Short answer", "Long answer", "File upload", "Data Consent", "Hidden", "Single choice"


class FormulierVeldOptie(TypedDict):
    caption: str
    value: str


class FormulierVeld(TypedDict):
    alias: str
    caption: str
    helpText: str
    id: str
    pattern: str
    patternInvalidErrorMessage: str
    preValues: list[FormulierVeldOptie]
    required: bool
    requiredErrorMessage: str
    settings: dict[str, Any]
    type: FormulierVeldType


class FormulierKolom(TypedDict):
    caption: str
    fields: list[FormulierVeld]


class FormulierFieldset(TypedDict):
    caption: str
    columns: list[FormulierKolom]


class FormulierPagina(TypedDict):
    caption: str
    fieldsets: list[FormulierFieldset]


class Formulier(TypedDict, total=False):
    id: str
    name: str
    pages: list[FormulierPagina]
    submitLabel: str
    messageOnSubmit: str
    gotoPageOnSubmitRoute: str | None


class FormulierBestand(TypedDict):
    fileName: str
    fileContents: str  # data URL, bijv. "data:application/pdf;base64,..."


class MailAlertItem(TypedDict, total=False):
    siteType: str
    postcode: str | None
    latitude: str | float | None
    longitude: str | float | None
    range: str | int | None
    crebocode: str | int | None
    label: str


class MailAlert(TypedDict, total=False):
    email: str
    isNewsletterSubscribed: bool
    items: list[MailAlertItem]


class Vertaling(TypedDict):
    key: str
    name: str
    value: str


class VertalingCategorie(TypedDict):
    localeCategory: str
    locales: list[Vertaling]


class Vertalingen(TypedDict):
    locales: list[VertalingCategorie]


class FilterDefinitieOptie(TypedDict, total=False):
    label: str
    value: str
    default: bool


class FilterDefinitie(TypedDict, total=False):
    __filtertype: str
    name: str
    filterName: str
    label: str
    placeholder: str
    source: str | None
    businessRole: str
    options: list[FilterDefinitieOptie]
