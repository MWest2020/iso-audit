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
- [ ] `src/iso_audit/reporting/local_report.py` — sectie 3 (Bevindingen) krijgt aan het begin een OFI-uitlegblok + top-5 thema-aggregatie­tabel
- [ ] `src/iso_audit/pipeline.py` — handmatige "lead-auditor aanbeveling"-sectie controleren op verboden woorden en herformuleren
- [ ] `src/iso_audit/pipeline.py` — `--report-only` flag toevoegen die bevindingen uit bestaande DB laadt en alleen rapport regenereert

## Validatie

- [ ] Dry-run met `--report-only` op bestaande s05 DB (output/audit_s10.db)
- [ ] Diff tussen oude en nieuwe management-summary visueel reviewen
- [x] Verboden-woorden-check geautomatiseerd: `_check_verboden_woorden` (woordgrens-regex) over de aanbevelingen-sectie + unit-tests (schoon/vuil/samenstelling). Logt waarschuwing bij hit i.p.v. crashen (boring & auditable)
- [ ] Marianne-akkoord op output vóór archivering van deze change

## Documentatie

- [ ] CHANGELOG.md entry met datum, wijziging, reden, validatie-status
- [ ] `audit/README.md` bijwerken: nieuwe schrijfregels expliciet documenteren als onderhoudsgids voor toekomstige prompt-aanpassingen
