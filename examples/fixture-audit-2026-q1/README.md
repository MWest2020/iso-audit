# Fixture: audit-2026-q1

Geanonimiseerde sample-set voor regressie- en snapshot-tests van de
classifier-keten. Adresseert milestone B taak 2.1.1.

## Doel

Een **byte-stabiele** input → output-baseline waartegen de gemigreerde
classifier in `src/iso_audit/classification/` continu wordt geverifieerd.

> Zie `tests/classification/test_findings_snapshot.py` (komt in 2.1.2)
> voor het regressie-mechanisme.

## Inhoud

| Bestand | Inhoud | Status |
|---|---|---|
| `generate_fixture.py` | Reproduceerbare generator vanuit bron-CSV | **klaar** |
| `findings.csv` | 20 geanonimiseerde audit-bevindingen, schema gelijk aan `Bevindingen_beide_v3.3_2026-05-05.csv` | **klaar** (2026-05-13) |
| `findings.expected.csv` | Antwoord-sleutel: `doc_id` + `classificatie` + `clausule` + `norm` | **klaar** (2026-05-13) |
| `documents/` | Geanonimiseerde document-bron-snippets (Drive / Miro) per fixture-rij | optioneel — pas relevant als classifier op rauwe document-tekst draait i.p.v. classified records |
| `sample-rapport.md` | Verwachte rapport-output (subset) na milestone B classifier-run | optioneel — pas in §2.5 reporting-migratie |

## Schema

Kolommen overgenomen uit het v3.3-bevindingen-export:

- `norm` — `9001` / `27001` / `beide`
- `clausule` — `5.11`, `8.16`, etc.
- `clausule_titel` — letterlijke titel uit normtekst (**niet** geanonimiseerd; geen PII)
- `classificatie` — `NC` / `OFI` / `positief` / `geen bevinding` (antwoord-veld)
- `thema` — categorisering (`Memo & afwijkingsregistratie`, `Logging & monitoring`, ...)
- `thema_bron` — `v2_keywords` / `llm` / ...
- `document_naam` — geanonimiseerd
- `herkomst` — `Drive` / `Miro`
- `beschrijving` — geanonimiseerd
- `onderbouwing` — geanonimiseerd
- `doc_id` — SHA-256 prefix (22 chars) van originele Drive-ID
- `doc_url` — `https://example.invalid/d/<hashed-id>/view`
- `classified_at` — vaste datum `2026-01-01T00:00:00Z` voor reproduceerbaarheid

## Anonimisatie-regels

1. **Persoonsnamen** → `Medewerker A`, `Medewerker B`, `Medewerker C`, ...
   (consistent binnen de fixture; mapping niet bewaard)
2. **Klant- en partner-namen** → `Klant X`, `Partner Y`
3. **Drive-IDs** → SHA-256 van originele ID, eerste 22 chars (Drive-formaat)
4. **URLs** → `https://example.invalid/<gehashed-id>/view`
5. **Memo-titels** met persoonsnamen → naam vervangen, structuur behouden
6. **E-mailadressen** → `<rol>@example.invalid` (bv. `auditor@example.invalid`)

## Selectie-criteria (≤20 rijen)

De fixture moet **representatief** zijn voor de echte dataset:

- ≥2 NC-rijen (één 9001, één 27001) — capability-2 traceability
- ≥6 OFI-rijen, verdeeld over top-3 thema's (memo, audit, logging)
- ≥4 positieve bevindingen
- ≥2 `herkomst=miro`-rijen (kleurconventie-validatie)
- ≥1 rij per `classificatie`-categorie
- Mix van clausules: §4, §5, §6, §8, §9, §10 (geen single-chapter fixture)

## Reproductie

```bash
python generate_fixture.py \
    --source ~/projects/Ops_to_Biz/output/audit_reports/Auditrapportage\ v3.3.\ 2026-05-05/Bevindingen_beide_v3.3_2026-05-05.csv
```

De generator schrijft `findings.csv` en `findings.expected.csv` deterministisch
op basis van de bron-CSV. Bij wijziging van bron-data: opnieuw uitvoeren en
de gewijzigde `findings.csv`-diff reviewen op anonimisatie-correctheid voor
commit.

## Bekende beperkingen

- **NC-coverage is asymmetrisch.** De huidige bron-CSV (v3.3) bevat 2 NC's,
  beide op ISO 27001. Het "≥1 9001-NC + ≥1 27001-NC"-criterium in het
  originele plan is daarom afgezwakt naar "≥2 NC". Synthetische 9001-NC's
  toevoegen zou de baseline vervuilen.
- **Vrije-tekst Drive-IDs.** De anonymizer ving Drive-ID's binnen URLs af.
  Naakte ID's in vrije tekst zijn in deze bron-set niet aangetroffen; mocht
  het in toekomstige fixtures wel voorkomen, dan een specifiekere pattern
  toevoegen aan `generate_fixture.py` (mengsel van letters+cijfers+
  streepjes, niet alleen lengte).
