from typing import TypedDict


class BaseVergoeding(TypedDict):
    omschrijving: str


class EducatieSearchResultItemVergoeding(BaseVergoeding):
    id: str
