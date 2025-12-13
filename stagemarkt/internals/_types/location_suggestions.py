from __future__ import annotations
from typing import TypedDict

from .base import LocatieSuggestieBodyDataItemType


class LocatieSuggestie(TypedDict):
    status: int
    body: LocatieSuggestieBody


class LocatieSuggestieBody(TypedDict):
    data: list[LocatieSuggestieBodyDataItem]


class LocatieSuggestieBodyDataItem(TypedDict):
    suggestie: str
    type: LocatieSuggestieBodyDataItemType
    plaats: LocatieSuggestieBodyDataItemPlaats | None


class LocatieSuggestieBodyDataItemPlaats(TypedDict):
    gemeente: str | None
    regio: str | None
    lat: float | None
    lon: float | None
    naam: str | None
    postcode: str | None
    provincie: str | None
