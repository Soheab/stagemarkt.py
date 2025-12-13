from __future__ import annotations
from typing import TypedDict


class OpleidingSuggestie(TypedDict):
    status: int
    body: OpleidingSuggestieBody


class OpleidingSuggestieBody(TypedDict):
    data: OpleidingSuggestieBodyData


class OpleidingSuggestieBodyData(TypedDict):
    hasNextPage: bool
    hasPreviousPage: bool
    pageNumber: int
    totalCount: int
    totalPages: int
    items: list[OpleidingSuggestieBodyDataItem]


class OpleidingSuggestieBodyDataItem(TypedDict):
    creboCode: int
    equivalenten: list[str]
    label: str
    synoniemen: list[str]
    value: str  # label (creboCode)
