# Tasks — audit-rapport-management-taal

## Voorbereiding

- [x] Feedback Marianne vastleggen in memory (`feedback_audit_rapport_taal.md`)
- [x] Before/after voorbeeld opstellen (`output/audit_reports/before_after_management_summary.md`)
- [ ] Voorbeeld voorleggen aan Marianne tijdens overleg + akkoord op nieuwe toon

## Code-wijzigingen

- [ ] `audit/report_generation.py` — `_management_summary_prompt` herschrijven (auditor-frame, SMART-blokken, jargon-vertaal-instructie, bridging-regel, verboden woorden)
- [ ] `audit/report_generation.py` — `_top3_aanbevelingen` herschrijven naar positieve template; verboden NC-woorden uitfilteren of expliciet niet meegeven aan LLM
- [ ] `audit/local_report.py` — sectie 3 (Bevindingen) krijgt aan het begin een OFI-uitlegblok + top-5 thema-aggregatie­tabel
- [ ] `audit/pipeline.py` — handmatige "lead-auditor aanbeveling"-sectie controleren op verboden woorden en herformuleren
- [ ] `audit/pipeline.py` — `--report-only` flag toevoegen die bevindingen uit bestaande DB laadt en alleen rapport regenereert

## Validatie

- [ ] Dry-run met `--report-only` op bestaande s05 DB (output/audit_s10.db)
- [ ] Diff tussen oude en nieuwe management-summary visueel reviewen
- [ ] Verboden-woorden-check geautomatiseerd: regex over gegenereerd rapport, faalt op "onvoldoende|ontoereikend|risico|lacune|gebrek|ontbreekt" binnen aanbevelingen-sectie
- [ ] Marianne-akkoord op output vóór archivering van deze change

## Documentatie

- [ ] CHANGELOG.md entry met datum, wijziging, reden, validatie-status
- [ ] `audit/README.md` bijwerken: nieuwe schrijfregels expliciet documenteren als onderhoudsgids voor toekomstige prompt-aanpassingen
