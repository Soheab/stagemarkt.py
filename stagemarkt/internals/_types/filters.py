from __future__ import annotations
from typing import TypedDict


class Filter(TypedDict):
    id: str
    options: list[FilterOption]


class FilterOption(TypedDict):
    hits: int
    id: str
    label: str
