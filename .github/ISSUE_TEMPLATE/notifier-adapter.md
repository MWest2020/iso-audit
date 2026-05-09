---
name: Notifier-adapter contribution
about: Nieuwe handoff-kanaal implementeren (Slack, Email, Teams, Mattermost, MCP-handoff)
labels: ["adapter", "notifiers"]
---

<!-- Notifier-adapters bieden een communicatiekanaal tussen integer-modus en de
     menselijke auditor. Een nieuwe notifier is pas mergeable wanneer
     onderstaande checklist volledig groen is. -->

## Welk kanaal?

<!-- Naam (kebab-case, e.g. "teams", "mattermost", "mcp-teams"), korte beschrijving
     van het kanaal, en authentication-mechanisme. -->

## Hoe vraagt je adapter een besluit?

<!-- Push-message met action-buttons, magic-link in e-mail, MCP-tool-call, anders?
     Beschrijf in 2-3 zinnen. -->

## Hoe vangt je adapter de respons op?

<!-- Webhook-callback, polling, lokaal portaal, anders? Welke action-shapes
     ondersteunt het kanaal en hoe mappen die naar `(decision_id, action,
     modified_payload)` voor de DecisionResolver? -->

## Protocol-conformance checklist

- [ ] Class implementeert `Notifier` Protocol uit `src/iso_audit/notifiers/base.py`
- [ ] `naam` class-attribute is uniek (lowercase, kebab-case)
- [ ] Twee methodes geïmplementeerd: `vraag_besluit`, `healthcheck`
- [ ] Bij identieke `Decision`-input genereren opeenvolgende calls unieke decision_ids
- [ ] Response-handler roept `DecisionResolver.resolve()` aan met de juiste shape
- [ ] mypy `--strict` rapporteert geen Protocol-violations

## Tests

- [ ] `tests/notifiers/test_<naam>.py` met adapter-specifieke scenarios
- [ ] `tests/notifiers/test_protocol_contract.py` parametrized contract-tests groen
- [ ] Externe API gemockt; geen echte calls in CI

## Documentatie

- [ ] `docs/notifiers/<naam>.md` met setup-instructies en env-vars
- [ ] Acceptable-risk-notities (TLS, token-expiratie, single-use, etc.) expliciet
- [ ] CHANGELOG-entry onder `[Unreleased]`

## Audit-trail

- [ ] Outbound message + inbound response gelogd voor reproduceerbaarheid
- [ ] `decisions.notifier_naam` wordt door de resolver correct gevuld
- [ ] Geen secrets gelogd

## Registratie

- [ ] `@register` decorator op class
- [ ] Adapter importeerbaar via `iso_audit.notifiers` package init
