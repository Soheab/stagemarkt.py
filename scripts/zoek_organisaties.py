"""Zoek naar organisaties en exporteer de resultaten."""

import asyncio
from pathlib import Path

from stagemarkt import (
    StagemarktClient,
    Straal,
)
from stagemarkt.utils import AttrField, to_excel


async def main() -> None:
    client = StagemarktClient()

    try:
        # Pas deze parameters aan
        plaats = "Amsterdam"
        crebocode = 25998  # Software developer
        straal = Straal.KM_15

        print(f"Zoeken naar organisaties voor crebo {crebocode} in '{plaats}'...")
        print("Debug: Verzenden van verzoek naar API...")

        organisaties = await client.zoek_organisaties(
            plaats=plaats,
            crebocode=crebocode,
            straal=straal,
            met_details=True,  # Haal details op voor telefoonnummer etc.
        )
        print("Debug: API-antwoord ontvangen")

        print(f"✓ {len(organisaties)} organisaties gevonden")

        if not organisaties:
            print("Geen organisaties gevonden.")
            return

        # Definieer kolommen met AttrField (correcte types)
        attributes = [
            AttrField("Naam").add("naam"),
            AttrField("Plaats").add("vestigingsadres.plaats"),
            AttrField("Straat").add("vestigingsadres.straat"),
            AttrField("Website").add("website"),
            AttrField("Email").add("email"),
            AttrField("Telefoon").add("telefoonnummer"),
            AttrField("Aantal Leerplaatsen").add("aantal_leerplaatsen"),
            AttrField("Leerbedrijf ID").add("leerbedrijf_id"),
        ]

        output_file = Path("organisaties_export.xlsx")

        to_excel(
            path=output_file,
            objects=organisaties,
            names=(None, attributes),  # pyright: ignore[reportArgumentType]
            include_empty=True,
        )

        print(f"✓ Geëxporteerd naar {output_file.absolute()}")

    finally:
        await client.afsluiten()


if __name__ == "__main__":
    asyncio.run(main())
