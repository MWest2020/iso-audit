# Source: Planning

> **Status:** spec klaar; implementatie in milestone B (verhuisd uit
> `Ops_to_Biz/audit/planning_ingest.py` + `gsa_client.py`).

Google Sheets-gebaseerde audit-planning als aparte bron. Conceptueel
losgekoppeld van Drive: planning is een operationeel document waar
auditor-besluiten in worden bijgehouden, niet een bewijsmateriaal-bron.

## Configuratie

| Env-var | Verplicht | Beschrijving |
|---|---|---|
| `GOOGLE_SERVICE_ACCOUNT_FILE` | ja | Pad naar service-account JSON-key (gedeeld met DriveSource) |
| `GOOGLE_IMPERSONATE_USER` | ja | Email die de service-account impersoneert |
| `AUDIT_PLANNING_SHEETS_ID` | ja | Spreadsheet-ID van de auditplanning |

## Scopes

- `https://www.googleapis.com/auth/spreadsheets.readonly`

## Aanroep

```bash
iso-audit pipeline --source planning --norm 27001 --mode autonoom
```
