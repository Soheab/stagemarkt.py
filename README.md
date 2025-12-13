# Stagemarkt.nl (onofficiële) Python wrapper

Dit is een **onofficiële** Python wrapper voor Stagemarkt.nl.

Voor zover bekend is er **geen publieke, officiële API-documentatie**. De gebruikte endpoints zijn reverse-engineered via de Network-tab in browser Developer Tools (educatief doel).

## Website

https://stagemarkt.nl

## Disclaimer

- Dit is een onofficieel project en heeft **geen enkele affiliatie** met Stagemarkt, SBB of enige gerelateerde organisatie.
- De API is **niet gedocumenteerd** en kan op elk moment zonder waarschuwing veranderen.
- Gebruik is volledig op eigen risico.
- Gebruik dit project verantwoordelijk en met respect voor de dienst.

## Documentatie

Alle onderdelen in deze repository zijn voorzien van docstrings.

## Voorbeelden (scripts)

De map `scripts/` bevat kant-en-klare voorbeelden:

- [`scripts/haal_stages_op.py`](scripts/haal_stages_op.py): haalt stages op en exporteert naar Excel.
- [`scripts/zoek_organisaties.py`](scripts/zoek_organisaties.py): zoekt organisaties en exporteert naar Excel.
- [`scripts/controleer_stage.py`](scripts/controleer_stage.py): haalt detail van één leerplaats en exporteert naar JSON.
- [`scripts/voorbeeld_met_filters.py`](scripts/voorbeeld_met_filters.py): gebruikt filters om zoekresultaten te verfijnen.

## Client API (kort)

- `zoek_stages(...)`: zoek stages per niveau, plaats, crebocode en straal.
- `zoek_organisaties(...)`: zoek organisaties met vergelijkbare criteria.
- `zoek_locaties(term)`: suggesties voor plaatsen/locaties.
- `haal_stage_detail(leerplaats_id)`: detail voor een specifieke stage.
- `haal_organisatie_detail(organisatie_id)`: detail voor een organisatie.
- `zoek_opleidingen(niveau, term, limiet)`: suggesties voor opleidingen.
- `zoek_studie_locaties(crebocode, lat, lon)`: studielocaties in de buurt.

## Exporters

- Voor Excel-export verwacht `to_excel` een `names=(title, attrs)` tuple waarbij `attrs` een `list[AttrSpec]` is.
- Gebruik `AttrField` om kolommen te definiëren; cast desnoods naar `list[AttrSpec]` om type checkers tevreden te stellen.
- Niet alle velden zijn altijd aanwezig; exporters ondersteunen `include_empty`.

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
