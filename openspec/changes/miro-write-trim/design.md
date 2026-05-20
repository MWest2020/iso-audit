# Design — miro-write-trim

## Scope & uitsluitingen

**In scope:** verwijderen van twee Python-modules die een Miro-bord
*creëren of muteren* (write API-calls), en hun tests. Plus de
bijbehorende OpenSpec change die de schrijf-flow als toekomstige feature
beschreef.

**Niet in scope:**

- MiroClient.post-methode in `client.py`: blijft als algemene HTTP-laag.
  Wordt na deze trim nergens meer gebruikt vanuit de productie-code,
  maar is geen onderhoudslast en bewaart optionaliteit.
- READ-pijp: `client.paginated_get` + `ingest.py` blijven onaangetast.
- Drive- en Jira-source-adapters: irrelevant voor deze change.

## Wat exact weg

| Pad | Regels | Tests | Rationale |
|---|---|---|---|
| `src/iso_audit/miro/board_setup.py` | 183 | 20 in `tests/miro/test_board_setup.py` | Auto-aanmaken audit-bord met frames per clausule + legende-sticky's. Miro-AI doet dit beter (auditor heeft real-time controle over layout). |
| `src/iso_audit/miro/interview.py` | 302 | 13 in `tests/miro/test_interview.py` | Interview-bord generator met sticky's per ongedekte clausule. Auditor doet dit zelf in Miro met een vraag-template. |

Totaal: 485 LOC + 33 tests weg.

## Wat exact blijft

| Pad | Reden |
|---|---|
| `src/iso_audit/miro/client.py` (`MiroClient`) | `paginated_get` is essentieel voor READ. `post` blijft als optionaliteit. |
| `src/iso_audit/miro/ingest.py` | De READ-pijp: `haal_notities_op`, `koppel_aan_clausules`, `merge_met_drive_bevindingen`. |
| `src/iso_audit/miro/__init__.py` | Exports zijn al beperkt tot client-laag; geen wijziging nodig. |
| `tests/miro/test_client.py` + `test_ingest.py` | Dekken de READ-pijp én de gedeelde MiroClient. |

## Decisions

### D1: `MiroClient.post` niet verwijderen

We laten `post` + `_post_once` in `client.py` staan, ook al wordt het
na deze change nergens meer aangeroepen vanuit de productie-code. Drie
redenen:

1. **Symmetrie & uitlegbaarheid:** een HTTP-laag met alleen GET is een
   raar contract; toekomstige lezers vragen zich af waarom er geen POST
   is.
2. **Goedkope optionaliteit:** ~30 regels code en wat tests onderhouden
   is goedkoper dan het later opnieuw moeten implementeren als blijkt
   dat we POST tóch ergens nodig hebben (bv. voor een notificatie-
   sticky op een bord bij een NC).
3. **Geen externe runtime-impact:** de methode is alleen actief bij
   aanroep; staat op zichzelf niet in de pipeline-call-stack.

Als bij latere review blijkt dat dit dood-code-bias is, kan POST
alsnog in een vervolg-trim weg.

### D2: Niet zelfde change doen voor `Ops_to_Biz/sessions/`

De `Ops_to_Biz/sessions/`-module is al verwijderd in commit `512c49a`
op Ops_to_Biz. Deze change in iso-audit is daar de natuurlijke
counterpart, niet een herhaling. Beide repos verlaten de write-flow
synchroon.

### D3: Geen migratie-handleiding "van Python naar Miro-AI"

De nieuwe docs (`docs/miro-auditor-bord-prompt.md`,
`docs/miro-interview-prompt.md`) zijn **alternatieven**, geen
migratie-paden. Wie het oude Python-pad nog op disk heeft, kan
'm draaien tot deze change merged is. Daarna is de auditor verplicht
de Miro-AI-route te lopen of een eigen bord op te bouwen.

### D4: Verifieerbaarheid via dry-run-cost identiek aan baseline

Na de trim moet `iso-audit pipeline --dry-run-cost` exact dezelfde
cijfers geven (152 docs, 73 calls, ~$0.33). Dit is de gouden test:
de pipeline raakt de write-modules niet aan, dus verwijderen mag
gerust. Elke afwijking is een bug in de pre-trim assumptie.

## Risico's & mitigaties

| Risico | Kans | Impact | Mitigatie |
|---|---|---|---|
| Een externe caller buiten dit repo importeerde `miro.board_setup` | Laag | Mid | Code blijft in git-historie; revert herstelt. Pre-check in tasks 2.1 + 2.2 (`grep -rn`) vangt interne refs. Externe afnemers zijn niet bekend (private repo, alleen Mark + 1 collaborator). |
| `MIRO_BOARD_ID` env-var wordt op WRITE-pad gebruikt | Laag | Laag | Variabele wordt nu via `MiroClient`-init voor READ gebruikt; behouden in `.env.example`. Geen wijziging nodig. |
| `tests/conftest.lege_registries` herlaadt `iso_audit.miro.*` modules | Mid | Mid | Verifieer met `grep -n "miro.interview\|miro.board_setup" tests/conftest.py` — als er reload-lines staan, weghalen samen met de modules. |
| Auditor verwacht het Python-pad in een lopende audit | Mid | Laag | De docs (4.1 + 4.2) bieden direct een Miro-AI-prompt als vervanging. Tussentijds kan de auditor een hand-getekend bord opzetten. |

## Acceptatiecriteria (machine-leesbaar)

- `git diff --name-only refactor/iso-audit-milestone-b..refactor/miro-write-trim`
  toont alleen: 2 deletes + 2 deletes + 1 archive-move + 2 docs-add + 1
  proposal-add.
- `pytest -q` exit 0, **649 passed** (was 682, ‐33).
- `pytest --cov=iso_audit --cov-report=term -q | tail -1` toont
  coverage **≥ 80%**.
- `iso-audit pipeline --source drive --norm 9001 --mode autonoom
  --dry-run-cost` retourneert exact 152 docs / 73 calls / ±$0.33.
