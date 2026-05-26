# iso-audit

> **Status:** milestone A + B + grootste deel C gemerged. Drie sources
> (Drive, Planning, Jira), één Sink (Drive), twee Notifiers (Slack, Email)
> en beide modes (autonoom, integer) draaien. Resterend werk: eerste
> end-to-end integer-run als M-C §3.6 acceptatie, daarna `v1.0.0`-tag.

Pluggable ISO 9001 + 27001 audit-pipeline met drie protocol-lagen
(sources, sinks, notifiers) en twee runmodes (autonoom, integer).

## Quick start

```bash
git clone https://github.com/MWest2020/iso-audit.git
cd iso-audit
uv sync --dev
uv run iso-audit --help
```

De CLI biedt `pipeline`, `doctor` en `setup-template` subcommands. Drie
verplichte flags: `--source`, `--mode`, en (bij `--mode integer`)
`--notifier`. Env-var-fallback voor cron — zie ARCHITECTURE.md
§"Configuratie".

## Architectuur

```
sources/  →  pipeline  →  modes  →  notifiers (integer)
                  ↓
                sinks  (publicatie)
```

Volledig plaatje in **[`ARCHITECTURE.md`](ARCHITECTURE.md)**. Het waarom
in **[`docs/missie.md`](docs/missie.md)**. Sessie-status en volgende-
stap in **[`MEMORY.md`](MEMORY.md)**.

## Documentatie

- **[`docs/missie.md`](docs/missie.md)** — drie capabilities en het rolconflict-frame
- **[`ARCHITECTURE.md`](ARCHITECTURE.md)** — protocol-lagen, registries, pipeline-flow
- **[`docs/sources/`](docs/sources/)** — per bron-adapter (drive, planning, jira, mcp, rest)
- **[`docs/sinks/`](docs/sinks/)** — schrijf-adapters
- **[`docs/notifiers/`](docs/notifiers/)** — handoff-kanalen (slack, email, teams, mattermost)
- **[`docs/modes.md`](docs/modes.md)** — autonoom vs integer en de zeven beslispunten

## Ontwikkeling

```bash
uv run pytest                        # tests
uv run ruff check .                  # lint
uv run ruff format --check .         # format-check
uv run mypy --strict src             # type-check
uv run bandit -r src                 # security
uv run pre-commit run --all-files    # alles
```

CI draait dezelfde vijf jobs parallel op elke PR.

## Bijdragen

PRs zijn welkom. Voor nieuwe Source- of Notifier-adapters: gebruik de
respectievelijke issue-templates onder
[`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/) — die forceren de
protocol-conformance-checklist.

OpenSpec-workflow voor substantiële wijzigingen: zie
[`CLAUDE.md`](CLAUDE.md).

## Licentie

Proprietary. Conduction. Open-source-publicatie is een mogelijke route
beschreven in [`docs/missie.md`](docs/missie.md) §"Risico's bij het tool zelf"
maar nog niet besloten.
