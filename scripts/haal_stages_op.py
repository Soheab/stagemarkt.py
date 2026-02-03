"""Haal alle stages op en exporteer naar Excel met specifieke kolommen."""

from typing import Literal
import argparse
import asyncio
from pathlib import Path

from stagemarkt import (
    Niveau,
    StagemarktClient,
    Straal,
)
from stagemarkt.utils import Field, FieldOption, maak_stagemarkt_link, maak_zoeklink, to_excel, to_json

parser = argparse.ArgumentParser()
parser.add_argument("--export", choices=["excel", "json"], default="excel", help="Export formaat: excel of json")

args = parser.parse_args()
export_formaat: Literal["xlsx", "json"] = "xlsx" if args.export == "excel" else "json"


async def main() -> None:
    client = StagemarktClient()

    try:
        niveau = Niveau.MBO_4
        plaats_postcode = "Amsterdam"
        crebocode = 25998
        straal = Straal.KM_50

        zelf_zoeklink = maak_zoeklink(
            niveau=niveau.value,
            straal=straal.value,
            crebocode=crebocode,
            plaats_postcode=plaats_postcode,
        )
        print(f"Zoeken naar stages (Niveau: {niveau.name}, Locatie: {plaats_postcode}, Straal: {straal.value}km)...")
        print(f"Zelf gemaakte zoeklink: {zelf_zoeklink}")
        print("Debug: Verzenden van verzoek naar API...")

        educaties = await client.zoek_stages(
            niveau=niveau, plaats=plaats_postcode, crebocode=crebocode, straal=straal, met_details=True, limiet=None
        )

        print("Debug: API-antwoord ontvangen")
        print(f"✓ {len(educaties)} educaties opgehaald")

        attributes = [
            Field("organisatie.naam", label="Bedrijfsnaam"),
            Field("adres.straat", label="Straat"),
            Field("adres.huisnummer", label="Huisnummer"),
            Field("adres.postcode", label="Postcode"),
            Field("adres.plaats", label="Plaats"),
            Field(label="Telefoonnummer").add("telefoon", fallback="organisatie.telefoonnummer"),
            Field(label="Email").add(
                "emailadres",
                fallback=FieldOption("organisatie.emailadres", fallback="organisatie.email"),
            ),
            Field(label="Website").add("website", fallback="organisatie.website"),
            Field("contactpersoon", label="Contactpersoon Naam"),
            Field("telefoon", label="Contactpersoon Tel"),
            Field(label="Contactpersoon Email").add(
                "emailadres",
                fallback=FieldOption("organisatie.emailadres", fallback="organisatie.email"),
            ),
            Field("omschrijving", label="Beschrijving"),
            Field(label="Stagemarkt Link").transform(
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

        output_file = Path(f"stages_export.{export_formaat}")
        exporter_meth = to_excel if export_formaat == "xlsx" else to_json

        kwargs = {}
        if export_formaat == "xlsx":
            kwargs["sheet_name"] = f"Stages-{crebocode}"

        exporter_meth(
            path=output_file,
            objects=educaties,
            names=("stages" if export_formaat == "json" else None, attributes),
            include_empty=True,
            **kwargs,
            sort="organisatie.naam",
        )

        print(f"✓ Geëxporteerd naar {output_file.absolute()}")

    finally:
        await client.afsluiten()


if __name__ == "__main__":
    asyncio.run(main())
