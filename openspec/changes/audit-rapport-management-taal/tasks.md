# Tasks — audit-rapport-management-taal

## Voorbereiding

- [x] Feedback Marianne vastleggen in memory (`feedback_audit_rapport_taal.md`)
- [x] Before/after voorbeeld opstellen (`output/audit_reports/before_after_management_summary.md`)
- [ ] Voorbeeld voorleggen aan Marianne tijdens overleg + akkoord op nieuwe toon

## Code-wijzigingen

> Paden gecorrigeerd na verhuizing uit `Ops_to_Biz`: `audit/` → `src/iso_audit/`.
> Ontwerpbesluit (2026-06-15): SMART-blokken staan in §3 Aanbevelingen, niet in
> de summary zelf (summary blijft kort, verwijst naar §3). Redactionele regels
> staan in versie-prompts `src/iso_audit/reporting/prompts/*.md`, niet in code.

- [x] `src/iso_audit/reporting/report_generation.py` — `_management_summary_prompt` herschreven: redactie naar `prompts/management_summary_v1.md` (auditor-frame, jargon-vertaal-instructie, bridging-regel), feiten blijven in code
- [x] `src/iso_audit/reporting/report_generation.py` — `_top3_aanbevelingen` als deterministische input-builder + nieuwe `_genereer_aanbevelingen` (SMART/positieve template via `prompts/aanbevelingen_v1.md`) + `_check_verboden_woorden`-gate op de output
- [x] `src/iso_audit/reporting/local_report.py` — OFI-uitleg (`_render_ofi_uitleg`, §2a) + top-5 thema-aggregatietabel (`_render_aanbevelingen`, §3) waren al geïmplementeerd in geëvolueerde code; geverifieerd dekkend voor req 5
- [x] ~~`src/iso_audit/pipeline.py` — handmatige "lead-auditor aanbeveling"-sectie~~ — **N.v.t.**: zo'n sectie bestaat niet in deze repo (stale carry-over uit Ops_to_Biz-layout, nooit gemigreerd). Gate `_check_verboden_woorden` bestaat nu en is herbruikbaar mocht de sectie ooit terugkomen
- [x] `--report-only` doorgetrokken naar de canonieke `iso-audit pipeline`-CLI (`cli.py`); `run_report_only` in `pipeline.py` bestond al. Laadt bevindingen uit DB, slaat ingest/classificatie/Drive/Miro over; `--source`/`--mode` niet vereist

## Validatie

- [ ] Dry-run met `--report-only` op bestaande s05 DB (output/audit_s10.db)
- [ ] Diff tussen oude en nieuwe management-summary visueel reviewen
- [x] Verboden-woorden-check geautomatiseerd: `_check_verboden_woorden` (woordgrens-regex) over de aanbevelingen-sectie + unit-tests (schoon/vuil/samenstelling). Logt waarschuwing bij hit i.p.v. crashen (boring & auditable)
- [ ] Marianne-akkoord op output vóór archivering van deze change

## Documentatie

- [ ] CHANGELOG.md entry met datum, wijziging, reden, validatie-status
- [x] Schrijfregels gedocumenteerd als onderhoudsgids: staan nu in de versie-prompts zelf (`prompts/*_v1.md`, met redacteur-notitie in de header) + `ONBOARDING.md` (prompts-map-regel). Dit vervangt het stale `audit/README.md`-pad
