# Source: Drive

> **Status:** spec klaar; implementatie in milestone B (verhuisd uit
> `Ops_to_Biz/audit/drive_ingest.py` + `gws_client.py`).

Google Drive als bron voor ISO-bewijsmateriaal. Read-only access via een
Google Workspace service-account met domain-wide delegation.

## Configuratie

| Env-var | Verplicht | Beschrijving |
|---|---|---|
| `GOOGLE_SERVICE_ACCOUNT_FILE` | ja | Pad naar service-account JSON-key |
| `GOOGLE_IMPERSONATE_USER` | ja | Email die de service-account impersoneert |
| `AUDIT_SOURCE_FOLDER_ID` | ja | Shared Drive root-ID (begint met `0A`) |

## Scopes

- `https://www.googleapis.com/auth/drive.readonly`
- `https://www.googleapis.com/auth/documents.readonly`

Schrijven naar Drive (rapport-publicatie) gebruikt een aparte `DriveSink`
in milestone C met andere scopes.

## Audit-trail

`healthcheck()` retourneert het `tenant`-veld als de Folder-ID. Externe
verifieerbaarheid: het ID is in elke Google Drive URL terug te vinden.

## Aanroep

```bash
iso-audit pipeline --source drive --norm 27001 --mode autonoom
```

Multi-source: `--source drive --source planning --source jira`.
