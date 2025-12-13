"""Haal alle stages op en exporteer naar Excel met specifieke kolommen."""

import asyncio
from pathlib import Path

from stagemarkt import (
    Niveau,
    StagemarktClient,
    Straal,
)
from stagemarkt.utils import AttrField, maak_stagemarkt_link, to_excel


async def main() -> None:
    client = StagemarktClient()

    try:
        niveau = Niveau.MBO_4
        plaats_postcode = "Amsterdam"
        crebocode = 25998
        straal = Straal.KM_25

        print(f"Zoeken naar stages (Niveau: {niveau.name}, Locatie: {plaats_postcode}, Straal: {straal.value}km)...")
        print("Debug: Verzenden van verzoek naar API...")

        educaties = await client.zoek_stages(
            niveau=niveau, plaats=plaats_postcode, crebocode=crebocode, straal=straal, met_details=True
        )

        print("Debug: API-antwoord ontvangen")
        print(f"✓ {len(educaties)} educaties opgehaald")

        attributes = [
            ("Bedrijfsnaam", "organisatie.naam"),
            ("Straat", "adres.straat"),
            ("Huisnummer", "adres.huisnummer"),
            ("Postcode", "adres.postcode"),
            ("Plaats", "adres.plaats"),
            ("Telefoonnummer", "telefoon"),
            AttrField("Email", "emailadres").fallback("organisatie.email"),
            AttrField("Website", "website").fallback("organisatie.website"),
            ("Contactpersoon Naam", "contactpersoon"),
            ("Contactpersoon Tel", "telefoon"),
            AttrField("Contactpersoon Email", "emailadres").fallback("organisatie.email"),
            AttrField("Stagemarkt Link").transform(
                lambda educatie: maak_stagemarkt_link(
                    educatie_id=educatie.leerplaats_id,
                    titel=educatie.title,
                    niveau=niveau.value,
                    educatie_type=1,
                    straal=straal.value,
                    crebocode=crebocode,
                    plaats_postcode=plaats_postcode,
                )
            ),
        ]

        output_file = Path("stages_export.xlsx")
        to_excel(
            path=output_file,
            objects=educaties,
            names=(None, attributes),
            include_empty=True,
        )

        print(f"✓ Geëxporteerd naar {output_file.absolute()}")

    finally:
        await client.afsluiten()


if __name__ == "__main__":
    asyncio.run(main())
