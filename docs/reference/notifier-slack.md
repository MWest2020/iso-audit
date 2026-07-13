---
status: draft
last_reviewed: 2026-07-13
---

# Notifier: Slack

> **Status:** spec klaar; implementatie in milestone C.

Slack als handoff-kanaal voor integer-modus. Block Kit-messages met
action-buttons (`Goedkeuren`, `Afwijzen`, `Aanpassen`, `Afbreken`).

## Configuratie

| Env-var | Verplicht | Beschrijving |
|---|---|---|
| `SLACK_BOT_TOKEN` | ja | OAuth-token van een Slack-app (`xoxb-…`) |
| `SLACK_AUDIT_CHANNEL` | ja | Channel-ID waar handoff-messages heen gaan |
| `SLACK_SIGNING_SECRET` | ja | Voor verificatie van button-callbacks via Events API |

## Slack-app setup

Eenmalig per workspace:

1. Maak een Slack-app via `api.slack.com/apps`
2. OAuth & Permissions → Bot Token Scopes:
   - `chat:write` (verzenden)
   - `channels:read` (channel resolve)
3. Interactivity & Shortcuts → enable, request-URL =
   `https://<jouw-host>/iso-audit/slack/interact` (handler die in
   milestone C wordt geïmplementeerd)
4. Install to Workspace; bewaar `SLACK_BOT_TOKEN` (begint met `xoxb-`)
5. Invite de bot in `#iso-audit-handoffs` (of welke channel je wilt)

## Audit-trail

Outbound Block Kit-messages én inbound button-payloads worden gelogd in
het pipeline-log. `decisions.notifier_naam = "slack"` voor cross-channel-
analyse later.

## Aanroep

```bash
iso-audit pipeline --source jira --source drive --mode integer --notifier slack
```
