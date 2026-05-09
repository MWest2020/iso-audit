---
name: Source-adapter contribution
about: Nieuwe Source-adapter implementeren (Drive, Jira, MCP, REST, of een andere bron)
labels: ["adapter", "sources"]
---

<!-- Source-adapters zijn een protocol-laag. Een nieuwe adapter is pas mergeable
     wanneer onderstaande checklist volledig groen is. Onvolledige PR's worden
     gesloten met verwijzing naar deze checklist. -->

## Welke bron?

<!-- Naam (kebab-case, e.g. "asana", "mcp-asana"), korte beschrijving van het
     bron-systeem, en authentication-mechanisme dat je gebruikt. -->

## Use-cases die je adapter dekt

<!-- Wat haalt het op? Documenten, findings, beide? Welk type
     ISO-bewijsmateriaal komt hier vandaan? -->

## Protocol-conformance checklist

- [ ] Class implementeert `Source` Protocol uit `src/iso_audit/sources/base.py`
- [ ] `naam` class-attribute is uniek (lowercase, kebab-case bij multi-woord)
- [ ] Vier methodes geïmplementeerd: `list_documents`, `fetch_content`, `list_findings`, `healthcheck`
- [ ] Geconfigureerd via env-vars en/of config-bestand bij pipeline-start (geen runtime-mutatie)
- [ ] Geen `set_*`-methodes of equivalent — configuratie immutable na init
- [ ] mypy `--strict` rapporteert geen Protocol-violations

## Tests

- [ ] `tests/sources/test_<naam>.py` met adapter-specifieke scenarios
- [ ] `tests/sources/test_protocol_contract.py` parametrized contract-tests groen
- [ ] Externe API gemockt; geen echte calls in CI

## Documentatie

- [ ] `docs/sources/<naam>.md` met setup-instructies, env-vars, voorbeelden
- [ ] `docs/sources/<naam>.md` benoemt audit-trail-implicaties (welke data komt waar vandaan)
- [ ] CHANGELOG-entry onder `[Unreleased]`

## Audit-trail

- [ ] Healthcheck retourneert `tenant`-veld dat extern verifieerbaar is
- [ ] Geen secrets gelogd

## Registratie

- [ ] `@register` decorator op class
- [ ] Adapter is importeerbaar via `iso_audit.sources` package init
