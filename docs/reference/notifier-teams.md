---
status: draft
last_reviewed: 2026-07-13
---

# Notifier: Teams

> **Status:** placeholder. Implementatie via eigen change-proposal
> `iso-audit-teams-notifier` wanneer de eerste afnemer (typisch
> gemeentelijke organisatie) erom vraagt.

Microsoft Teams als handoff-kanaal voor integer-modus. Adaptive
Cards-equivalent van Slack Block Kit.

## TODO

- Adapter implementeert `Notifier` Protocol via Microsoft Graph API
- Adaptive Cards met action-buttons
- Webhook voor inbound action-callbacks
- Authenticatie via Azure AD app-registration
- Mapping naar `(decision_id, action, modified_payload)` voor de
  DecisionResolver — dezelfde shape als Slack

Wachten op concrete vraag-vanuit-praktijk.
