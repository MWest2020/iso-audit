---
name: Bug report
about: Onverwacht gedrag, regressie, of crash
labels: ["bug"]
---

## Wat ging er mis?

<!-- Eén zin. Verwacht gedrag vs werkelijk gedrag. -->

## Reproductie

```
# Het commando dat je draaide, inclusief flags en env-vars (gemaskeerd voor secrets)
iso-audit pipeline --norm 27001 --source drive --mode autonoom
```

## Versie

- iso-audit versie: <!-- `iso-audit --version` -->
- Python: <!-- `python --version` -->
- OS / shell:

## Logs / output

<!-- Plak relevante logs. Verwijder API-tokens en credentials. -->

## Effect op audit-trail

<!-- Heeft deze bug data in `iso_audit.db` (decisions, classifications) gecorrumpeerd? -->

- [ ] Geen impact op DB
- [ ] DB-impact, beschrijving:
