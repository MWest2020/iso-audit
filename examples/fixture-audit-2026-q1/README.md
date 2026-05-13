# Fixture: audit-2026-q1

Geanonimiseerde sample-set voor regressie- en snapshot-tests van de
classifier-keten. Adresseert milestone B taak 2.1.1.

## Doel

Een **byte-stabiele** input → output-baseline waartegen de gemigreerde
classifier in `src/iso_audit/classification/` continu wordt geverifieerd.

> Zie `tests/classification/test_findings_snapshot.py` (komt in 2.1.2)
> voor het regressie-mechanisme.

## Inhoud (zodra ingevuld)

| Bestand | Inhoud | Status |
|---|---|---|
| `findings.csv` | ≤20 rijen geanonimiseerde audit-bevindingen, schema gelijk aan `Bevindingen_beide_v3.3_2026-05-05.csv` | **TODO** |
| `findings.expected.csv` | Verwachte `parsed_klasse` + `parsed_clausule` per `doc_id`/`herkomst` | **TODO** |
| `documents/` | Geanonimiseerde document-bron-snippets (Drive / Miro) per fixture-rij | **TODO** |
| `sample-rapport.md` | Verwachte rapport-output (subset) na milestone B classifier-run | **TODO** |

## Schema

Kolommen overgenomen uit het v3.3-bevindingen-export:

- `norm` — `9001` / `27001` / `beide`
- `clausule` — `5.11`, `8.16`, etc.
- `clausule_titel` — letterlijke titel uit normtekst
- `classificatie` — `NC` / `OFI` / `positief` / `geen bevinding`
- `thema` — categorisering (`memo & afwijkingsregistratie`, `logging & monitoring`, ...)
- `thema_bron` — `regel-based` / `llm`
- `document_naam` — geanonimiseerd
- `herkomst` — `drive` / `miro`
- `beschrijving` — geanonimiseerd
- `onderbouwing` — geanonimiseerd
- `doc_id` — gehasht (geen Drive-IDs in fixture)
- `doc_url` — placeholder URL `https://example.invalid/...`
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

## Workflow voor data-vulling

1. Selecteer 20 rijen uit
   `Ops_to_Biz/output/audit_reports/Auditrapportage v3.3. 2026-05-05/Bevindingen_beide_v3.3_2026-05-05.csv`
   volgens bovenstaande criteria.
2. Pas anonimisatie-regels toe (script of handmatig — script aanbevolen voor reproduceerbaarheid).
3. Plaats resultaat in `findings.csv`; bouw `findings.expected.csv` uit dezelfde rijen
   met enkel `doc_id` + `parsed_klasse` + `parsed_clausule`.
4. Voor `documents/`: kopieer bijbehorende Drive-doc tekst (geanonimiseerd; alleen
   relevante alinea's) als `<doc_id>.md`.

## Tegenwoordige beperking

Deze fixture is een **skeleton** — data wordt gevuld in een aparte commit
zodra de anonimisatie-mapping is afgestemd. Tot dan kan
`test_findings_snapshot.py` als `pytest.mark.skip` aangezet worden met
duidelijke marker.
