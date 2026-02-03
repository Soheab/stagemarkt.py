"""Voorbeeldscript dat laat zien hoe je filters gebruikt bij het zoeken naar educaties."""

import asyncio
from pathlib import Path
from sys import path

from stagemarkt import (
    EducatieFilters,
    Leerweg,
    Niveau,
    StagemarktClient,
    Straal,
)
from stagemarkt.utils import Field, to_excel


async def main() -> None:
    client = StagemarktClient()

    try:
        # Parameters
        niveau = Niveau.MBO_4
        plaats_postcode = "Amsterdam"
        crebocode = 25998  # Software developer
        straal = Straal.KM_15

        # Maak filters aan
        filters = EducatieFilters(
            leerwegen=[Leerweg.BOL],  # Alleen BOL (schoolgebaseerd leren)
            trefwoorden=["software"],  # Zoek naar "software" gerelateerde opleidingen
        )

        print(f"Zoeken naar stages met filters (Niveau: {niveau.name})...")
        print(f"Debug: Filters toepassen: {filters}")
        print("Debug: Verzenden van verzoek naar API...")

        educaties = await client.zoek_stages(
            niveau=niveau,
            plaats=plaats_postcode,
            crebocode=crebocode,
            straal=straal,
            filters=filters,
            met_details=True,
        )

        print("Debug: API-antwoord ontvangen")
        print(f"✓ {len(educaties)} gefilterde educaties opgehaald")

        if not educaties:
            print("Geen educaties gevonden met deze filters.")
            return

        # Exporteer naar Excel (gebruik Field)
        attributes = [
            Field("organisatie.naam", label="Bedrijfsnaam"),
            Field("title", label="Titel"),
            Field("leerweg", label="Leerweg"),
            Field("adres.plaats", label="Plaats"),
            Field("organisatie.email", label="Email"),
            Field("organisatie.website", label="Website"),
        ]

        output_file = Path("stages_filtered_export.xlsx")
        to_excel(
            path=output_file,
            objects=educaties,
            names=(None, attributes),  # pyright: ignore[reportArgumentType]
            include_empty=True,
        )

        print(f"✓ Geëxporteerd naar {output_file.absolute()}")

    finally:
        await client.afsluiten()


if __name__ == "__main__":
    asyncio.run(main())
