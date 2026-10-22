from __future__ import annotations

from typing import TypedDict


class Regio(TypedDict):
    id: str
    naam: str


class OrganisatieSuggestieItem(TypedDict):
    label: str
    value: str


class OrganisatieSuggestie(TypedDict):
    filters: None
    items: list[OrganisatieSuggestieItem]
