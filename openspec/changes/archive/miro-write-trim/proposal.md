# miro-write-trim

## Why

Miro heeft sinds eind 2025 ingebouwde AI om boards te genereren uit
prompts en templates. Het automatisch opzetten van een auditor-bord of
interview-bord via onze eigen Python-code (`iso_audit.miro.board_setup`
en `iso_audit.miro.interview`) automatiseert werk dat de auditor zelf
in een paar minuten doet met een goede prompt-template. De onderhouds-
last (Miro REST API-contract, rate-limits, kleur-conventies,
positie-berekeningen, ~475 LOC + ~300 LOC tests) is niet meer
evenredig aan het nut.

De ISO-use-case voor Miro is in essentie **lezen**:

- auditor plakt sticky-notes op een Miro-bord tijdens documentanalyse;
- iso-audit ingest leest die notities (`haal_notities_op`), classificeert
  ze op kleur (groen/oranje/rood → positief/OFI/NC) en koppelt ze aan
  clausules op basis van labels of tekst (`koppel_aan_clausules`);
- de classifier consumeert ze samen met Drive-bevindingen.

Schrijven (auto-board-aanmaak) is daarbij een gemak, geen capability
uit de missie (zie `docs/missie.md`).

## What Changes

Verwijderen:

- `src/iso_audit/miro/board_setup.py` (183 regels, 31% cov)
- `src/iso_audit/miro/interview.py` (302 regels, 47% cov)
- `tests/miro/test_board_setup.py` (20 tests)
- `tests/miro/test_interview.py` (13 tests)
- `openspec/changes/miro-kennissessie-generator/` → archive

Behouden:

- `src/iso_audit/miro/client.py` (MiroClient HTTP-laag) — `paginated_get`
  is essentieel voor READ; `post` blijft als kapstok voor toekomstige
  features maar wordt nergens in de pipeline meer aangeroepen.
- `src/iso_audit/miro/ingest.py` (`haal_notities_op`,
  `koppel_aan_clausules`, `merge_met_drive_bevindingen`) — de READ-pijp.
- `src/iso_audit/miro/__init__.py` — exports blijven gelijk.
- `tests/miro/test_client.py` + `test_ingest.py` — READ-paden.

Toevoegen:

- `docs/miro-auditor-bord-prompt.md` — een korte handleiding + voorbeeld-
  prompt die de auditor kan plakken in Miro-AI om in één klik een
  audit-bord met frames per clausule + legende-sticky's op te zetten.
  Vervangt het Python-automatisme.

## Impact

- **Tests**: 682 → ~649 (33 weg, geen nieuwe). Coverage blijft ≥ 80% omdat
  de verwijderde modules de laagste coverage hadden (31% / 47%).
- **Pipeline**: ongewijzigd. De pipeline gebruikt `haal_documenten_op`
  (Drive) + `haal_notities_op` (Miro, READ). Geen call naar
  `board_setup` of `interview` vanaf `pipeline.py`.
- **Backwards-compat**: geen — de twee modules werden niet vanuit een
  CLI-subcommand aangeroepen. Wel scripts onder `Ops_to_Biz/sessions/`
  gebruikten ze als inspiratie; die zijn al verwijderd uit Ops_to_Biz.
- **Auditor-workflow**: minimaal verschil. Nu eerst een Miro-AI-prompt
  draaien (1–2 min) i.p.v. een Python-script (ook 1–2 min). De auditor
  heeft meer controle over de board-layout en kan in real-time aanpassen.
