# Tasks — miro-write-trim

## 1. Baseline vastleggen

- [ ] 1.1 Quality-gate volledig groen op `refactor/iso-audit-milestone-b`
  vóór wijzigingen: `uv run ruff check && uv run mypy --strict src/ &&
  uv run bandit -r src/ -ll && uv run pytest -q` — verwacht **682 passed,
  1 skipped**. Noteer de hash van de baseline-commit in deze task-regel
  bij uitvoering.
- [ ] 1.2 Functionele baseline: `uv run iso-audit doctor` — verifieer
  dat alle 4 sources + 2 notifiers correct gedetecteerd zijn met de
  juiste healthcheck-status (creds aanwezig of niet, ongewijzigd).
- [ ] 1.3 Pipeline-baseline: `uv run iso-audit pipeline --source drive
  --norm 9001 --mode autonoom --dry-run-cost`. Noteer:
  - aantal docs (Drive na MIME-filter) — verwacht 152
  - aantal Claude-calls — verwacht 73
  - kostenschatting — verwacht ~$0.33
  Deze cijfers moeten **identiek** zijn aan eind van de change.

## 2. Verwijder write-modules incrementeel

Elke stap apart committen op `refactor/miro-write-trim`-branch zodat
bij regressie de blame eenvoudig is.

- [ ] 2.1 Verwijder `src/iso_audit/miro/interview.py` +
  `tests/miro/test_interview.py`.
  - **Pre-check**: `grep -rn "from iso_audit.miro.interview\|import
    iso_audit.miro.interview" src/ tests/` moet leeg zijn (interview
    wordt nergens geïmporteerd door overige modules).
  - **Dry-run na verwijdering**: full test-suite → verwacht **669 passed**
    (682 − 13). `uv run iso-audit pipeline --dry-run-cost` → identieke
    cijfers als 1.3.

- [ ] 2.2 Verwijder `src/iso_audit/miro/board_setup.py` +
  `tests/miro/test_board_setup.py`.
  - **Pre-check**: `grep -rn "from iso_audit.miro.board_setup\|import
    iso_audit.miro.board_setup" src/ tests/` moet leeg zijn. Let op
    constanten als `FRAME_HEIGHT`, `FRAME_GAP_Y` die hierin staan —
    als die elders geïmporteerd werden, gaat de grep dat tonen.
  - **Dry-run na verwijdering**: full test-suite → verwacht **649 passed**
    (669 − 20). Pipeline `--dry-run-cost` → identieke cijfers als 1.3.

- [ ] 2.3 Verifieer `src/iso_audit/miro/__init__.py` ongewijzigd
  (exports `MiroClient`, `MiroError`, `MiroRateLimitError`). Geen
  imports van weggehaalde modules in `__all__`.

- [ ] 2.4 Coverage-check: `uv run pytest --cov=iso_audit --cov-report=term
  -q | tail -5` — verwacht overall **≥ 80%** (de weggehaalde modules
  hadden de laagste coverage, dus overall % stijgt). Geen module
  onder 70%.

## 3. OpenSpec opruimen

- [ ] 3.1 Verhuis `openspec/changes/miro-kennissessie-generator/` naar
  `openspec/changes/archive/miro-kennissessie-generator/` (write-flow
  expliciet bevroren). Commit-message vermeldt de reden + verwijst
  naar deze change.
- [ ] 3.2 Update `openspec/changes/archive/iso-refactor/tasks.md` indien
  nodig (referenties naar `board_setup` / `interview` weghalen).

## 4. Documentatie — alternatief voor write-pad

- [ ] 4.1 Schrijf `docs/miro-auditor-bord-prompt.md`:
  - korte uitleg dat het Python-automatisme is verwijderd;
  - voorbeeld-prompt die in Miro-AI geplakt kan worden om een audit-
    bord met 5 frames (Context / Leiderschap / Planning / Uitvoering
    / Evaluatie) + legende-sticky's (groen/oranje/rood) op te zetten;
  - hoe de auditor de Miro-board-ID kopieert en in `MIRO_BOARD_ID`
    env-var zet voor de READ-pijp.
- [ ] 4.2 Schrijf `docs/miro-interview-prompt.md` als equivalent voor de
  interview-stap (vragen per ongedekte clausule). Inhoud: vraag-
  template die de auditor 1-op-1 doorloopt of in Miro neerzet als
  sticky-notes per clausule.

## 5. Acceptatie

- [ ] 5.1 Pre-merge dry-run: `uv run iso-audit pipeline --source drive
  --norm 9001 --mode autonoom --dry-run-cost`. **Resultaat moet
  byte-identiek** zijn aan de baseline uit 1.3 (zelfde aantal docs,
  zelfde 73 calls, zelfde $0.33 schatting).
- [ ] 5.2 Volledige test-suite groen (649 passed, ~1 skipped).
- [ ] 5.3 CI-pipeline groen op de PR (lint + format + typecheck +
  security + test + coverage ≥ 70%).
- [ ] 5.4 Coverage ≥ 80% overall (was 81%; verwacht +1–2pp omdat de
  modules met laagste coverage weg zijn).
- [ ] 5.5 README/CLAUDE.md: noem `docs/miro-auditor-bord-prompt.md` en
  `docs/miro-interview-prompt.md` als referenties voor de auditor-
  workflow; verwijder verwijzingen naar het oude Python-write-pad.
- [ ] 5.6 Tag `v0.3.0-beta` (of vergelijkbaar) — eerste post-M-C trim.

## 6. Veiligheidsnet — rollback-recept

Als blijkt dat de write-modules tóch nog door iets/iemand worden
gebruikt:

- [ ] 6.1 De code blijft in de git-historie beschikbaar. Een revert
  van de twee delete-commits zet alles terug. Het bestand
  `docs/miro-auditor-bord-prompt.md` wordt dan een aanvulling i.p.v.
  vervanging.
- [ ] 6.2 Mocht een specifieke functie (bv. `_grid_position` in
  `interview.py`) wel herbruikbaar blijken, dan migreren naar een
  klein utility-module met expliciete naam + tests in plaats van
  hele bestanden te herstellen.
