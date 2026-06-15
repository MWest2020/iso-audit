"""Google Workspace authenticatie via service account.

Scope-strategie (least privilege):
    - `drive.readonly`     — documenten lezen uit Drive
    - `drive.file`         — alleen bestanden schrijven die de app zelf aanmaakt
    - `documents.readonly` — Google Docs lezen
    - `documents`          — Google Docs schrijven
    - `spreadsheets`       — Google Sheets lezen en schrijven
    - `presentations`      — Google Slides aanmaken
    - `gmail.send`         — e-mail versturen
    - `calendar`           — Calendar-uitnodigingen aanmaken

De echte toegangsmuur is het Drive-deelbeleid: deel het service account
UITSLUITEND met de "Interne Audits"-map. Bestanden buiten die map zijn
voor het account simpelweg onzichtbaar.

Gemigreerd uit `Ops_to_Biz/audit/auth.py` per milestone B §2.2.2.
"""

from __future__ import annotations

import os
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Lezen: alleen de Drive-map die expliciet gedeeld is met het service account.
_READ_SCOPES: list[str] = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
]

# Schrijven: alleen bestanden die de app zelf aanmaakt (drive.file).
_WRITE_SCOPES: list[str] = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
]

CREDS_ENV_VAR = "GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE"


def _get_credentials(scopes: list[str]) -> Any:
    """Laad de service-account-credentials voor de gevraagde scopes.

    Pad van het JSON-keyfile komt uit env-var `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE`.
    Returntype is `Any` omdat `google.oauth2.service_account` geen
    runtime-stubs heeft die mypy --strict tevreden stellen.
    """
    creds_file = os.environ.get(CREDS_ENV_VAR)
    if not creds_file:
        raise OSError(f"{CREDS_ENV_VAR} niet ingesteld in .env")
    # google-auth ships zonder volledige type-stubs voor service_account;
    # de call is wel runtime-typed, maar mypy --strict ziet hem als untyped.
    return service_account.Credentials.from_service_account_file(  # type: ignore[no-untyped-call]
        creds_file, scopes=scopes
    )


def drive_read_service() -> Any:
    """Drive-service met alleen leesrechten."""
    return build("drive", "v3", credentials=_get_credentials(_READ_SCOPES))


def drive_write_service() -> Any:
    """Drive-service voor aanmaken van bestanden (drive.file scope)."""
    return build("drive", "v3", credentials=_get_credentials(_WRITE_SCOPES))


def docs_read_service() -> Any:
    """Google Docs-service met leesrechten."""
    return build("docs", "v1", credentials=_get_credentials(_READ_SCOPES))


def docs_write_service() -> Any:
    """Google Docs-service voor app-eigen documenten."""
    return build("docs", "v1", credentials=_get_credentials(_WRITE_SCOPES))


def sheets_service() -> Any:
    """Google Sheets-service (lezen + schrijven)."""
    return build("sheets", "v4", credentials=_get_credentials(_WRITE_SCOPES))


def slides_service() -> Any:
    """Google Slides-service voor presentatie-aanmaken."""
    return build("slides", "v1", credentials=_get_credentials(_WRITE_SCOPES))


def gmail_service() -> Any:
    """Gmail-service voor `gmail.send`-scope."""
    return build("gmail", "v1", credentials=_get_credentials(_WRITE_SCOPES))


def calendar_service() -> Any:
    """Google Calendar-service voor uitnodigingen."""
    return build("calendar", "v3", credentials=_get_credentials(_WRITE_SCOPES))
