---
status: draft
last_reviewed: 2026-07-13
---

# Source: Jira

> **Status:** spec klaar; implementatie in milestone C.

Jira Cloud als bron van bevindingen. Relevant voor ISO 27001 §10
(verbetering) en §8.16 (incidentregistratie): open issues die als
afwijking, incident of verbetervoorstel zijn gelabeld worden bevindingen
in de pipeline.

## Configuratie

| Env-var | Verplicht | Beschrijving |
|---|---|---|
| `JIRA_BASE_URL` | ja | `https://<workspace>.atlassian.net` |
| `JIRA_EMAIL` | ja | Service-account email |
| `JIRA_TOKEN` | ja | API-token (read-only scope) |
| `JIRA_AUDIT_JQL` | nee | JQL-filter; default: `labels = audit AND status != Closed` |

## Audit-trail

`healthcheck()` retourneert het `tenant`-veld als `JIRA_BASE_URL`. Externe
verifieerbaarheid via Atlassian admin-console: welke issues door de
service-account benaderd worden staat in het audit-log van Jira zelf.

## Aanroep

```bash
iso-audit pipeline --source jira --norm 27001 --mode integer --notifier slack
```

Voor multi-source met Drive secundair:

```bash
iso-audit pipeline --source jira --source drive --norm 27001 --mode integer --notifier slack
```
