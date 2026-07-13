---
status: draft
last_reviewed: 2026-07-13
---

# Sinks — schrijf-adapters

Sink-adapters publiceren rapport-output of stuur-en-vergeet notificaties
naar doelsystemen (Drive voor rapport-publicatie, mogelijk later
Confluence voor management-summary, etc.).

## Status

| Adapter | Status | Aangekomen |
|---|---|---|
| Drive | Spec klaar | Implementatie in milestone C |
| (toekomstig) | — | Eigen change-proposals zodra een doel zich aandient |

## Sink versus Notifier

Sinks zijn one-shot: payload erin, resultaat eruit, klaar. Voor
interactieve handoff (auditor moet beslissen) zie de `notifier-*`-pagina's
onder [`reference/`](./).

## Sink-adapter implementeren

Volg `.github/ISSUE_TEMPLATE/source-adapter.md` (analoog patroon).
Verschillen:

- Implementeer `iso_audit.sinks.base.Sink`-protocol (`send`, `healthcheck`).
- Accepteer één of meer payload-types (`ReportPayload`,
  `NotificationPayload`, eventueel `MirrorPayload` voor capability-3-werk).
- Registreer via `@iso_audit.sinks.register`.
- Schrijf `tests/sinks/test_<naam>.py` met scenarios voor elk
  payload-type dat je adapter accepteert.
- Documenteer in `docs/reference/sink-<naam>.md`.
