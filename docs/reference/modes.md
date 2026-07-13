---
status: draft
last_reviewed: 2026-07-13
---

# Pipeline modes: autonoom en integer

> **Status:** spec klaar; volledige implementatie in milestone C. In
> milestone A bestaat alleen de `Decision` dataclass en de `Mode` Protocol-
> stub.

iso-audit kent twee runmodes. Beide gebruiken dezelfde codebase; verschil
zit in het beleid bij beslismomenten.

## Autonoom

Voor cron-/CI-runs en geautomatiseerde maandelijkse audits. Geen mens-
input gevraagd; pipeline draait end-to-end zonder onderbreking.

`AutonoomMode.beslis(decision)` accepteert het voorstel direct, behalve
voor `delete_data` — dat is altijd geblokkeerd in autonoom (de pipeline
slaat de delete over en logt het).

## Integer

Voor audit-runs waarbij de auditor in-the-loop moet zijn op kritieke
beslismomenten (ISO 19011-conformiteit én capability-3-data-bron).
Pipeline pauzeert bij hoog-risico beslissingen, escaleert via een
`Notifier`, blokkeert tot de auditor reageert.

`IntegerMode.beslis(decision)` regels:

- `risico="laag"` — accepteer voorstel autonoom
- `risico="midden"` — accepteer autonoom **tenzij** `context["confidence"] < 0.7`
  of `context["vraag_bevestiging"] == True` — dan escaleren
- `risico="hoog"` — altijd escaleren naar Notifier

## De zeven beslispunten

| Punt | Risico | Autonoom | Integer |
|---|---|---|---|
| `ingest_scope` | laag | accepteer geconfigureerde scope | tonen bij flag, bevestigen |
| `merge_drive_miro` | laag | auto | auto |
| `classify_finding` | midden | LLM-output accepteren | escaleer bij low-confidence |
| `assign_clausule` | midden | regel-based | escaleer bij low-confidence |
| `generate_report_section` | hoog | LLM-output direct | concept, mens-review verplicht |
| `send_report` | hoog | direct via Sink | sign-off via Notifier |
| `delete_data` | hoog | blokkeer altijd, log | mens-bevestigd via Notifier |

Toevoegen van nieuwe beslispunten gaat via change-proposal — pipeline-
code mag het niet ad-hoc uitbreiden.

## Modi en de missie

`AutonoomMode` persisteert alleen `risico="hoog"` beslissingen in de
`decisions`-tabel. Reden: laag- en midden-risico besluiten in autonoom-
runs zijn altijd `voorstel == besluit` zonder mens-input — geen
analytische waarde voor de spiegel-laag (capability 3 uit
[`explanation/missie.md`](../explanation/missie.md)).

Concreet: **autonoom-runs leveren geen volle capability-3-data**. Voor
patroon-analyse over auditor-besluiten zijn integer-runs nodig.

## Crash-recovery

`IntegerMode` schrijft pending Decisions naar SQLite (`decisions`-tabel)
voordat hij de Notifier aanroept. Bij pipeline-crash + restart query't de
pipeline op `(audit_id, status="pending")` en hervat in plaats van
opnieuw te escaleren. Voorkomt dubbele Slack-messages of email-magic-
links.

## CLI

```bash
# Autonoom (typisch cron)
iso-audit pipeline --source drive --mode autonoom

# Integer met Slack-handoff
iso-audit pipeline --source drive --source jira --mode integer --notifier slack

# Integer met Email-handoff
iso-audit pipeline --source drive --mode integer --notifier email
```

`--mode` is verplicht (geen default). `--notifier` is verplicht alleen
bij `--mode integer`. Beide hebben `ISO_AUDIT_DEFAULT_*`-env-var-fallback
voor cron-context.
