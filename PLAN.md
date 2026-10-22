# Stagemarkt API: findings, current state and rename plan

Working notes for `stagemarkt.py`. Everything below was checked against the live API
(stagemarkt.nl) and the site's own JavaScript bundles in October 2026.

Contents:

1. [API reference](#1-api-reference)
2. [What changed in the library](#2-what-changed-in-the-library)
3. [Not verified / known gaps](#3-not-verified--known-gaps)
4. [Rename and grouping plan](#4-rename-and-grouping-plan)
5. [Open questions](#5-open-questions)

---

## 1. API reference

### 1.1 Endpoints

All under `https://stagemarkt.nl/api`.

| Endpoint | Method | Purpose | Client method (current name) |
|---|---|---|---|
| `query-hub/education-search` | GET | Search stages (leerplaatsen) + filter facets | `zoek_stages`, `haal_filter_opties` |
| `query-hub/organization-search` | GET | Search leerbedrijven + filter facets | `zoek_organisaties`, `haal_filter_opties(organisaties=True)` |
| `query-hub/education-detail?id=` | GET | Stage detail | `haal_stage_detail` |
| `query-hub/organization-detail?id=` | GET | Leerbedrijf detail | `haal_organisatie_detail` |
| `query-hub/locatie-suggesties?term=` / `?lat=&lon=` | GET | Location autocomplete | `zoek_locaties` |
| `query-hub/opleiding-suggesties?term=&opleidingsniveau=&pageSize=` | GET | Opleiding autocomplete | `zoek_opleidingen` |
| `query-hub/organisatie-suggesties?term=` | GET | Organisation name autocomplete | `zoek_organisatienamen` |
| `query-hub/regios` | GET | All 35 regions | `haal_regios` |
| `query-hub/study-locations?crebo=&lat=&lon=` | GET | Schools offering an opleiding nearby (no longer used by the site, still works) | `zoek_studie_locaties` |
| `umbraco/filters` | GET | Filter definitions from the CMS | `haal_filter_definities` |
| `umbraco/content?route=` | GET | Raw CMS content of a page | `haal_pagina` |
| `umbraco/translations` | GET | All site texts | `haal_vertalingen` |
| `umbraco/form?id=` | GET | Form definition | `haal_formulier` |
| `stages/preview?token=` | GET | Preview of an unpublished stage (plain text `not-found` if invalid) | `haal_stage_preview` |
| `mail-alerts/mail-alerts?mailGuid=` | GET | A saved mail alert | `haal_mail_alert` |
| `forms/submit` | POST | Submit any form: `{"id": <form id>, "values": {...}}` | `solliciteer`, `stel_vraag_*`, `meld_probleem`, `maak_mail_alert`, `wijzig_mail_alert` |

Not Stagemarkt: `/api/v2/video/` and `/api/player` are Vimeo (embedded videos).
The homepage only calls `query-hub/regios` at runtime; its CMS content is just info cards.

### 1.2 Search parameters

| Param | Values | education-search | organization-search |
|---|---|---|---|
| `crebocode` | int | yes | yes (optional) |
| `opleidingsniveau` | 0 (pro/vso/vmbo), 1–4 | accepted, no visible effect with a crebocode | no effect |
| `plaatsPostcode` | place name or postcode | yes | yes |
| `straal` | km (site: 5, 10, 15, 25, 50, 75) | yes | yes, **required** when `plaatsPostcode` is set (otherwise 0 results) |
| `locatieType` | `Plaats`, `Postcode`, `Regio`, `Land` | yes | yes |
| `regio` | region id (`/regios`) | yes | **ignored** |
| `sort` | see 1.3 | yes | yes |
| `termen` | space-separated keywords | yes | yes |
| `soortBedrijf` | SBI id, repeatable (OR) | yes | yes |
| `bedrijfsgrootte` | id, repeatable (OR on education, first value only on organization) | yes | yes |
| `sectoren` | id | ignored | yes |
| `kenmerken` | id, repeatable (AND) | yes | ignored |
| `leerweg` | BOL/BBL id, **one value only** (two → HTTP 500) | yes | ignored |
| `vergoedingen` | id, repeatable | yes | – |
| `startInMonths` | int: starts within N months (site: 1, 3, 6) | yes | – |
| `alleWerkprocessenUitvoerbaar` | `true`/`false` | yes | – |
| `land` | ISO country code | – | yes |
| `buitenland` | `true` → foreign companies only | ignored | yes |
| `organisatie` | (part of) company name | – | yes |
| `aantalLeerplaatsen` | only `0` is valid → companies **without** open stages | – | yes |
| `page`, `pageSize` | ints | pageSize up to 5000 | **pageSize max 20** (more → only 10 items) |

Parameters that do nothing: `direction`, `amp`, `type` (1/2), `buitenlandseBedrijven`, `siteId`.
`organization-search` caps `totalCount` at 10000, but deeper pages still load.

Old parameter names the library used to send and the API silently ignores:
`range` (→ `straal`), `niveau` (→ `opleidingsniveau`), `companyType` (→ `soortBedrijf`),
`sector` (→ `sectoren`), `learningPath` (→ `leerweg`), `keyword` (→ `termen`).

### 1.3 Sort values (`sort`)

Validated by the API (zod enum): `RELEVANTIE`, `ACTUALITEIT`, `AFSTAND`, `SALARIS`, `BAANKANS`,
`STARTDATUM`, `ALFABETISCHE_VOLGORDE_ORGANISATIENAAM`, `OMGEKEERDE_ALFABETISCHE_VOLGORDE_ORGANISATIENAAM`,
`BEDRIJFSGROOTTE`, `BPVO_REGISTRATIES`, `AANTAL_LEERBANEN`.

Shown on the site: `/stages` → ACTUALITEIT (default), AFSTAND, STARTDATUM.
`/leerbedrijven` → RELEVANTIE (default), A-Z, Z-A, ACTUALITEIT.

### 1.4 Search pages on the site

| Route | Data source | Notes |
|---|---|---|
| `/stages` | education-search | filters: leerweg, soortBedrijf, bedrijfsgrootte, startInMonths, kenmerken, alleWerkprocessenUitvoerbaar, sectoren, termen |
| `/leerbedrijven` | organization-search | filters: straal, land, soortBedrijf, bedrijfsgrootte, sectoren, kenmerken, termen |
| `/buitenlandse-bedrijven` | organization-search with `buitenland=true` | filters: land, soortBedrijf, sectoren, bedrijfsgrootte, kenmerken, termen |

### 1.5 Location selection

Picking a location suggestion on the site sets three params together:
`plaatsPostcode` = place name (or postcode), `regio` = region id (only for `Regio` results or ambiguous
place names), `locatieType` = the suggestion's type.

### 1.6 Forms

`POST /api/forms/submit` with body `{"id": "<form id>", "values": {<alias>: <value>}}`.

| Form | Id | Fields |
|---|---|---|
| Sollicitatie | `e2f49d2f-76b5-428c-ae44-a2b274573833` | naam, emailadres, emailadres2, telefoonnummer, berichtOfMotivatie, onlineCV, cVEnofMotivatiebrief (files), dataConsent, hidden: leerplaatsId, contactPersonEmail, siteType |
| Vraag over stage | `661a0c6c-6bc0-48fc-bbc8-91565a19d1e6` | naam, emailadres, emailadres2, telefoonnummer, berichtOfMotivatie, dataConsent, hidden: leerplaatsId, contactPersonEmail, siteType |
| Vraag aan leerbedrijf | `074a37d5-7ab3-488a-8ea6-6b421f45e5f2` | same, with hidden `leerbedrijfId` (organisation GUID) instead of `leerplaatsId` |
| Klopt iets niet | `f4e9aae4-c029-4c3c-b403-1b200e98c7da` | watKloptErNiet (choice), berichtOfMotivatie, naam, emailadres, emailadres2, dataConsent, hidden: leerplaatsId, siteType |
| Mail alert aanmaken | `62028b5ce4304ca0a2bcc8555f77cc0d` | email, newsletter, dataConsent, items |
| Mail alert wijzigen | `63feada0949e4783be28016b4cc322fe` | email (hidden), newsletter, dataConsent, itemsToDelete |

Details taken from the site's code:

- Consent and checkbox fields are the string `"True"`.
- Files: list of `{"fileName": ..., "fileContents": "data:<mime>;base64,..."}`; site accepts .pdf/.docx/.doc/.txt, max 5 MB.
- `siteType` is `"2"` (first character of the CMS setting `umbracoFormSiteType` = `"2 | stagemarkt"`).
- `contactPersonEmail` is the `emailadres` from the stage/organisation detail endpoint.
- There is a hidden honeypot field `website` that must stay empty.
- Mail alert items: `{siteType, postcode, latitude, longitude, range, crebocode, label}`, all strings.
- The update form identifies the alert by `email` (from `GET mail-alerts?mailGuid=`), not by the guid.
- Form ids come from the CMS and can change.

### 1.7 Response shape changes found

- `locatie-suggesties` now returns a plain list (was `{status, body: {data}}`).
- `opleiding-suggesties` now returns `{filters, items, totalCount, ...}` (was `body.data`).
- Detail endpoints still return a single object.
- New fields on detail responses: `acroniem`, `sbi`, `opleidingsgebieden`, `oudeLeerbedrijfIds`,
  `kvKNaam`/`kvKNummer`/`kvKVestigingsNummer` (always null so far), `heeftProfiel`, `werkprocessen`.

---

## 2. What changed in the library

### 2.1 Bug fixes

| Problem | Fix |
|---|---|
| `straal` sent as `range` → any search with a plaats returned 0 organisaties | sends `straal` |
| niveau sent as `niveau` → `zoek_opleidingen` ignored the level | sends `opleidingsniveau` |
| `EducatieFilters` sent `companyType`/`sector`/`learningPath`/`keyword` → no filter ever applied | correct names |
| `zoek_locaties` crashed (`AttributeError`) | model accepts the new list shape |
| `zoek_opleidingen` returned nothing | model accepts the new shape |
| `limiet` not respected (`limiet=45` → 60) | paginator trims to the limit |
| Stages fetched 20 per page | 100 per page (organisations stay at 20, the API max) |

### 2.2 New search options

- `zoek_stages`: `sortering`, `locatie_type`, `regio`.
- `zoek_organisaties`: `sortering`, `locatie_type`, `niveau`, `organisatie`, `buitenland`,
  `alleen_zonder_leerplaatsen`; `crebocode` optional.
- `EducatieFilters`: `bedrijfsgroottes`, `kenmerken`, `vergoedingen`, `landen`, `start_binnen_maanden`,
  `alle_werkprocessen_uitvoerbaar`; `from_url` reads both current and legacy param names.

### 2.3 New methods

`zoek_organisatienamen`, `haal_regios`, `haal_filter_opties`, `haal_filter_definities`, `haal_pagina`,
`haal_vertalingen`, `haal_formulier`, `haal_stage_preview`, `haal_mail_alert`, `maak_mail_alert`,
`wijzig_mail_alert`, `solliciteer`, `stel_vraag_over_stage`, `stel_vraag_aan_leerbedrijf`, `meld_probleem`.
`zoek_locaties` also accepts `lat`/`lon`.

All form methods require `toestemming=True` and validate file type/size before sending.

### 2.4 New enums

`Sortering`, `Bedrijfsgrootte`, `VergoedingSoort`, `ProbleemSoort`, `StartBinnen`, `Regio` (35),
`Land` (110), `FormulierSoort`, `FormulierVeldType`, `FilterType`.
Extended: `Sector` (19), `Kenmerk`, `SoortBedrijf`, `Niveau.PRO_VSO_VMBO`, `LocatieType.LAND`.
Every parameter that takes an enum also accepts the raw string/number.

### 2.5 New models

`ZoekFilter`, `ZoekFilterOptie`, `FilterDefinitie`, `Formulier`, `FormulierVeld`, `MailAlert`,
`MailAlertItem` (with `van_locatie(...)`), `StagePreview`, `RegioInfo`.
`OrganisationDetail` gained `sbi`, `acroniem`, `opleidingsgebieden`.

### 2.6 Checks done

- Search result counts match the website: 247 (leerbedrijven Amsterdam 10 km), 98 (2–9 medewerkers),
  52 (software), 8 (zorg), 10/12/26/315/167 (stages).
- Every form payload matches the live form definition (no unknown fields, no missing required fields),
  with the POST stubbed out.
- `test3.py` runs every new method; form submits are stubbed and only print the payload.
- ruff passes; pyright: no new errors (touched files went from 13 errors at `HEAD` to 1).

---

## 3. Not verified / known gaps

- **No form was actually submitted.** Server acceptance of `forms/submit` is unconfirmed.
  Safest first real test: `maak_mail_alert` to your own address, or `meld_probleem`.
- `haal_mail_alert` / `wijzig_mail_alert` need a real `mailGuid`; the response model is based on the site's code.
- `haal_stage_preview` needs a real token; same caveat.
- `zoek_stages(educatie_type=...)`, `zoek_stages(buitenlandse_bedrijven=...)` and
  `zoek_organisaties(leerweg=...)` are ignored by the API; kept only for compatibility.
- `SoortBedrijf` is a selection; the API only lists the 10 most common options per search.
- `Land` lists countries that had leerbedrijven at time of writing.
- Nothing is committed yet.

---

## 4. Rename and grouping plan

The package is at `0.1.0`, so breaking changes are acceptable. Names that existed before this round of
work keep a deprecated alias (with `DeprecationWarning`) until 0.2; names added in this round are
renamed outright.

Callers to update: `README.md`, `scripts/locatie_autocomplete.py`, `scripts/voorbeeld_met_filters.py`,
`test3.py`. (`test.py` and `test2.py` are scratch files and are left alone.)
Exporters only use attribute paths (`Field("organisatie.naam")`), so class renames don't affect them.

### Step 1 — Main client (`StagemarktClient`)

| Now | New | Alias? |
|---|---|---|
| `zoek_stages` | unchanged | – |
| `zoek_organisaties` | unchanged | – |
| `haal_stage_detail` | unchanged | – |
| `haal_organisatie_detail` | unchanged | – |
| `zoek_locaties` | `suggereer_locaties` | yes |
| `zoek_opleidingen` | `suggereer_opleidingen` | yes |
| `zoek_organisatienamen` | `suggereer_organisaties` | no (new) |
| `zoek_studie_locaties` | `zoek_opleiders` | yes |
| `haal_regios` | unchanged | – |
| `haal_filter_opties(organisaties=True)` | `haal_filter_opties(soort=ZoekSoort.ORGANISATIES)` with new enum `ZoekSoort` (`STAGES`, `ORGANISATIES`) | no (new) |

### Step 2 — Group rarely used parts into namespaces

New file `stagemarkt/groepen.py` with `WebsiteGroep` and `MailAlertGroep`, both sharing the client's
`HTTPClient`:

```python
client.website.filters()           # was haal_filter_definities
client.website.pagina("/stages")   # was haal_pagina
client.website.teksten()           # was haal_vertalingen
client.website.formulier(soort)    # was haal_formulier
client.website.stage_preview(tok)  # was haal_stage_preview

client.mail_alerts.haal(guid)      # was haal_mail_alert
client.mail_alerts.maak(...)       # was maak_mail_alert
client.mail_alerts.wijzig(...)     # was wijzig_mail_alert
```

`solliciteer`, `stel_vraag_over_stage`, `stel_vraag_aan_leerbedrijf` and `meld_probleem` stay on the
main client. All grouped methods are new, so no aliases.

### Step 3 — Align `HTTPClient` names with the client

Internal, straight rename: `zoek_educaties` → `zoek_stages`, `haal_locaties` → `suggereer_locaties`,
`haal_educatie_detail` → `haal_stage_detail`, `haal_studie_locaties` → `zoek_opleiders`, and so on,
so each client method calls a method with the same name.

### Step 4 — Models

| Now | New | Alias? |
|---|---|---|
| `EducatieFilters` | `ZoekFilters` | yes |
| `EducationDetail` | `StageDetail` | yes |
| `OrganisationDetail` (+ `…Erkenning`, `…Kwalificatie`, `…Person`, `…Equivalent`) | `OrganisatieDetail` (+ `…Persoon`, etc.) | yes |
| `StudyLocation` | `Opleider` | yes |
| `Educatie` | unchanged for now (see open question 3) | – |

Attributes stay the same. Files are renamed to match (`education_detail.py` → `stage_detail.py`, etc.);
internal `_types` are left alone.

### Step 5 — Update callers and docs

- `README.md`: new names, the grouping, and a short "renamed in 0.2" section.
- `scripts/locatie_autocomplete.py`, `scripts/voorbeeld_met_filters.py`, `test3.py`: new names.

### Step 6 — Verify

- `ruff check` / `ruff format`.
- pyright: no new errors compared to `HEAD`.
- Run `test3.py` and the live checks; counts must still match (247 / 98 / 52 / 12 / 315).
- Old names still work and emit a `DeprecationWarning`.

### Step 7 — Commits

1. The API work so far (fixes, filters, endpoints, enums).
2. The renames and grouping (separate, so it can be reverted on its own).

---

## 5. Open questions

1. **Aliases or a clean break?** The plan keeps deprecated aliases for names that existed before; since
   it's 0.1.0, everything could also just be renamed.
2. **Group mail alerts?** `client.mail_alerts.*`, or keep `haal_`/`maak_`/`wijzig_mail_alert` on the
   main client next to `solliciteer`?
3. **Rename `Educatie` to `Stage`?** Completes the "stage everywhere" cleanup, but it's the biggest change.
