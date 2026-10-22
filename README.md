# Stagemarkt.py (onofficiële) Python wrapper

Dit is een **onofficiële** Python wrapper voor https://stagemarkt.nl.

Voor zover bekend is er **geen publieke, officiële API-documentatie**. De gebruikte endpoints zijn reverse-engineered via de Network-tab in browser Developer Tools.

## Disclaimer

- Dit is een onofficieel project en heeft **geen enkele affiliatie** met Stagemarkt, SBB of enige gerelateerde organisatie.
- De API is **niet gedocumenteerd** en kan op elk moment zonder waarschuwing veranderen.
- Gebruik is volledig op eigen risico.
- Gebruik dit project verantwoordelijk en met respect voor de dienst.

## Documentatie

Alle onderdelen in deze repository zijn voorzien van docstrings.

## Installatie

Benodigdheden:
- Python 3.12+
- [Git](https://git-scm.com/) (voor installatie via GitHub)

```bash
python -m pip install "stagemarkt.py @ git+https://github.com/Soheab/stagemarkt.py"
```

## Voorbeelden (scripts)

De map `scripts/` bevat kant-en-klare voorbeelden:

- [`scripts/haal_stages_op.py`](scripts/haal_stages_op.py): haalt stages op en exporteert naar Excel.
- [`scripts/zoek_organisaties.py`](scripts/zoek_organisaties.py): zoekt organisaties en exporteert naar Excel.
- [`scripts/controleer_stage.py`](scripts/controleer_stage.py): haalt detail van één leerplaats en exporteert naar JSON.
- [`scripts/voorbeeld_met_filters.py`](scripts/voorbeeld_met_filters.py): gebruikt filters om zoekresultaten te verfijnen.

## Client API (kort)

- `zoek_stages(...)`: zoek stages per niveau, plaats/postcode of regio, crebocode, straal en sortering.
- `zoek_organisaties(...)`: zoek (erkende) leerbedrijven, o.a. op naam, sortering, buitenland en
  `alleen_zonder_leerplaatsen` ("Erkende bedrijven met mogelijk een plek").
- `zoek_locaties(term, lat=, lon=)`: suggesties voor plaatsen, postcodes en regio's.
- `zoek_organisatienamen(term)`: autocomplete voor organisatienamen.
- `haal_regios()`: alle regio's (voor `zoek_stages(regio=...)`).
- `haal_filter_opties(...)`: alle filteropties met aantallen voor een zoekopdracht, zoals het filtermenu
  op de website (bedrijfssoort, bedrijfsgrootte, sector, land, leerweg, kenmerken, vergoedingen, ...).
- `haal_stage_detail(leerplaats_id)`: detail voor een specifieke stage.
- `haal_organisatie_detail(organisatie_id)`: detail voor een organisatie.
- `zoek_opleidingen(niveau, term, limiet)`: suggesties voor opleidingen.
- `zoek_studie_locaties(crebocode, lat, lon)`: studielocaties in de buurt.
- `haal_filter_definities()`, `haal_pagina(route)`, `haal_vertalingen()`: filterinstellingen, CMS-inhoud en teksten
  van de website.
- `haal_formulier(id)`: velden van een formulier.
- `haal_stage_preview(token)`: voorbeeldweergave van een stage via een preview-token.
- `haal_mail_alert(mail_guid)`, `maak_mail_alert(...)`, `wijzig_mail_alert(...)`: mail alerts (opgeslagen
  zoekopdrachten); gebruik `MailAlertItem.van_locatie(...)` om een zoekopdracht te maken.

### Formulieren versturen

Deze methodes versturen **echt** een e-mail naar een leerbedrijf of SBB, precies zoals de formulieren op de website.
Ze vereisen `toestemming=True` (akkoord met de privacyverklaring van SBB).

- `solliciteer(leerplaats_id, ...)`: solliciteer op een stage, optioneel met CV/motivatiebrief (.pdf, .docx, .doc,
  .txt; max. 5 MB per bestand).
- `stel_vraag_over_stage(leerplaats_id, ...)` en `stel_vraag_aan_leerbedrijf(organisatie_id, ...)`: stel een vraag.
- `meld_probleem(leerplaats_id, ...)`: meld dat er iets niet klopt aan een stage (`ProbleemSoort`).

Filters gaan via `EducatieFilters` (bedrijfssoorten, sectoren, leerwegen, trefwoorden, bedrijfsgroottes,
kenmerken, vergoedingen, landen, `start_binnen_maanden`, `alle_werkprocessen_uitvoerbaar`). Niet elk filter
werkt op beide zoekopdrachten; zie de docstring. `EducatieFilters.from_url` leest ook een URL van stagemarkt.nl.

## Exporters

- Voor Excel-export verwacht `to_excel` een `names=(title, attrs)` tuple waarbij `attrs` een `list[Field]` is.
- Gebruik `Field` om kolommen te definiëren (intern opgebouwd uit `FieldOption`).
- Niet alle velden zijn altijd aanwezig; gebruik `include_empty=False` om lege waarden te negeren.

## Rate limiting & performance

- Gebruik `limiet` spaarzaam. Grote of onbeperkte resultaten kunnen traag zijn.
- Overweeg caching of lokale opslag voor herhaalde queries.

## Bekende beperkingen

- Endpoints en datamodellen zijn reverse-engineered; breaking changes zijn mogelijk.

## Licentie

Deze repository valt onder een **restrictieve licentie**.

- Je mag de software alleen gebruiken voor persoonlijke, niet-commerciële, educatieve doeleinden.
- Je mag de software **niet aanpassen** (geen wijzigingen, forks of afgeleide werken) en **niet verspreiden**.
- Productie- of publieke inzet is alleen toegestaan met voorafgaande expliciete toestemming en een verplichte notice/attributie.

Zie [`LICENSE`](LICENSE). Door dit project te gebruiken ga je akkoord met deze voorwaarden.

## Contact

Voor vragen of suggesties: gebruik GitHub issues.
