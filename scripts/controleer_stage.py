"""Haal details op voor een specifieke leerplaats ID."""

import asyncio
from pathlib import Path

from stagemarkt import StagemarktClient
from stagemarkt.utils import JSONExporter


async def main() -> None:
    client = StagemarktClient()

    try:
        # Pas dit ID aan naar het ID dat je wilt controleren
        # Dit is het leerplaatsId (GUID)
        leerplaats_id = "8e1bf027-f865-4bea-b0a2-c5c00572f21a-25998"

        print(f"Details ophalen voor leerplaats {leerplaats_id}...")
        print("Debug: Verzenden van verzoek naar API...")

        details = await client.haal_stage_detail(leerplaats_id=leerplaats_id)

        print("Debug: API-antwoord ontvangen")
        if details:
            print(f"✓ Details gevonden voor: {details.title}")
            print(f"   Organisatie: {details.organisatie.naam if details.organisatie else 'Onbekend'}")
            print(
                (
                    f"   Adres: {details.adres.straat if details.adres else ''} "
                    f"{details.adres.huisnummer if details.adres else ''}, "
                    f"{details.adres.plaats if details.adres else ''}"
                )
            )

            # Exporteer naar JSON voor inspectie
            output_file = Path(f"stage_{leerplaats_id}.json")
            exporter = JSONExporter()
            exporter.export(output_file, [details])
            print(f"✓ Details opgeslagen in {output_file.absolute()}")
        else:
            print("Geen details gevonden of fout bij ophalen.")

    finally:
        await client.afsluiten()


if __name__ == "__main__":
    asyncio.run(main())
