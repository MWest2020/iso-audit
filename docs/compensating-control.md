# Compenserende beheersmaatregel — Audit Log

> Status: actief vanaf v0.1.0-alpha. Eigenaar: repo-owner (MWest2020).
> Hertoetsing: bij elke upgrade van de GitHub-tier of organisatie-migratie.

## Aanleiding

`openspec/changes/iso-refactor/tasks.md` § 1.1.4 vereist dat de Audit Log
van GitHub wordt ingeschakeld om wijzigingen aan repository-instellingen,
toegangsrechten en branch-protection-regels traceerbaar vast te leggen.

De **Audit Log API** is alleen beschikbaar op de Enterprise-tier (organisatie
op GitHub Enterprise Cloud of Enterprise Server). Deze repository is een
**privé-repo onder een persoonlijk account** (`MWest2020`). Het persoonlijke
account heeft alleen toegang tot de **Security Log** voor het eigen account
(gebeurtenissen op user-niveau, niet repo-instellingen).

Deze beheersmaatregel beschrijft de compenserende controles waarmee het
auditdoel van § 1.1.4 wordt afgedekt zonder Enterprise-tier.

## Auditdoel (te borgen)

Aantoonbaar maken — bij interne of externe audit — dat wijzigingen aan:

1. **Repository-instellingen** (private/public, default branch, merge-opties)
2. **Branch-protection-regels** (required reviewers, required checks,
   force-push-restrictie, signed-commits-vereiste)
3. **Toegangsrechten** (collaborators, deploy keys, secrets, tokens)
4. **CI/CD-workflows** (`.github/workflows/`, secrets-binding)

... bewust en door een geautoriseerde actor zijn aangebracht, op een
herleidbaar tijdstip.

## Compenserende controles

### C1 — Repository-instellingen en branch-protection als code

Branch-protection-regels worden niet alleen in de GitHub-UI gezet, maar
**ook gedocumenteerd** in deze repo onder `docs/branch-protection.md`
(referentie van de live-instelling) en zijn reproduceerbaar via `gh api`-
commando's vastgelegd in `docs/branch-protection-setup.sh`. Wijzigingen aan
de live-instelling die afwijken van het gedocumenteerde "expected state"
zijn detecteerbaar via periodieke `gh api` drift-check (zie C5).

### C2 — Verplichte PR-workflow voor élke wijziging

Branch-protection op `main` verbiedt directe pushes en force-pushes en eist
≥1 PR-review. Hierdoor bestaat van elke wijziging:

- Een PR met titel, beschrijving en review-trail (auteur + reviewer + tijdstip)
- De gemergde commit met PR-referentie in de message
- CI-status (lint/format/typecheck/security/test) als gate

De PR + commit-trail vervangt het Audit-Log-pad voor wijzigingen aan code,
workflows en branch-protection (zolang die in PR-vorm gebeuren).

### C3 — Signed commits (zodra geconfigureerd)

Branch-protection eist signed commits vanaf het moment dat de repo-owner
GPG- of SSH-signing heeft geconfigureerd (zie ook `docs/signing-setup.md`).
De handtekening bewijst auteurschap; in combinatie met C2 is elke wijziging
gekoppeld aan een geverifieerde identiteit.

> **Open punt:** de initial-commit (`6fba351` — milestone A scaffolding) is
> niet ondertekend. Toekomstige commits moeten dat wel zijn; deze
> compensating-control wordt aangevuld zodra signing-config actief is.

### C4 — CHANGELOG als handmatige audit-trail

Volgens Keep-a-Changelog-format wordt elke wijziging met inhoudelijke impact
in `CHANGELOG.md` vastgelegd, met datum en beschrijving. Dit is een
*read-only* trail voor reviewers die geen toegang tot de PR-historie hebben
(bv. tijdens externe audit waar alleen de archive van de repo wordt overhandigd).

### C5 — Periodieke drift-check (kwartaal)

Eens per kwartaal — gepland als onderdeel van de interne audit-cyclus —
draait de repo-owner:

```bash
gh api /repos/MWest2020/iso-audit/branches/main/protection > /tmp/protection.json
diff <(jq -S . /tmp/protection.json) <(jq -S . docs/branch-protection-expected.json)
```

Afwijkingen worden via PR teruggebracht naar de gedocumenteerde state. Het
diff-resultaat wordt als bijlage bij de interne-audit-rapportage bewaard.

### C6 — Account-niveau Security Log

Voor wijzigingen die buiten de PR-workflow vallen (bv. transfer van repository,
wijziging van repo-eigenaar, MFA-wijziging, token-aanmaak) wordt de **Security
Log** van het persoonlijke account geraadpleegd. Deze is beschikbaar via:

```
https://github.com/settings/security-log
```

Bij externe audit-vraag wordt een export van de relevante periode bijgevoegd.

## Migratiepad naar Enterprise

Zodra deze repo overgaat naar een organisatie op Enterprise-tier:

1. Activeer Audit Log API.
2. Vervang C5 (handmatige drift-check) door geautomatiseerde Audit-Log-export.
3. Markeer deze beheersmaatregel als "vervangen door Audit Log per <datum>"
   in `CHANGELOG.md` — bestand blijft staan voor audit-historie.

## Verwijzingen

- `openspec/changes/iso-refactor/tasks.md` § 1.1.4 — eis
- `docs/missie.md` — capability 2 (reproduceerbaarheid + traceability)
- GitHub-docs: [Audit log for your enterprise](https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/about-the-audit-log-for-your-enterprise)
