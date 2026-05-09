# Notifier: Mattermost

> **Status:** placeholder. Implementatie via eigen change-proposal
> `iso-audit-mattermost-notifier` wanneer een open-source-bewuste
> afnemer erom vraagt.

Mattermost als handoff-kanaal voor integer-modus. Interactive messages
met action-buttons.

## TODO

- Adapter implementeert `Notifier` Protocol via Mattermost REST API
- Interactive message attachments met buttons
- Slash command of incoming webhook voor action-callbacks
- Authenticatie via personal access token of bot account
- Mapping naar `(decision_id, action, modified_payload)` voor de
  DecisionResolver

Wachten op concrete vraag-vanuit-praktijk.
