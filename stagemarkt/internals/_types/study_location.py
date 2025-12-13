from __future__ import annotations
from typing import TypedDict

from .adres import StudyLocationVestigingsAdres


class StudyLocationResult(TypedDict):
    locationName: str
    schoolName: str
    emailadres: str
    telefoonnummer: str
    website: str
    logoUrl: str
    vestigingsadres: StudyLocationVestigingsAdres
