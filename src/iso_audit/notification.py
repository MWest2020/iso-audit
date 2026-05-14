"""Notificatie — Google Calendar uitnodigingen en optionele Gmail via `gws` CLI.

Alle verzendacties vereisen expliciete bevestiging van de auditor.

Gemigreerd uit `Ops_to_Biz/audit/notification.py` per milestone B §2.2.2.
Implementatie via externe `gws` CLI is bewust ongewijzigd; toekomstige
refactor naar Sink/Notifier-protocol komt in milestone C.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess  # nosec B404 — gws CLI uitvoeren is de bedoelde flow
from datetime import date, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


def _bevestig(actie: str, ontvangers: list[str]) -> bool:
    """Vraag expliciete bevestiging vóór elke verzendactie.

    Wrapt `input()` zodat tests deze functie kunnen monkeypatchen.
    """
    print(f"\n{'=' * 60}")
    print(f"BEVESTIGING VEREIST: {actie}")
    print("Ontvangers/deelnemers:")
    for ontvanger in ontvangers:
        print(f"  - {ontvanger}")
    invoer = input("Bevestig verzending? [ja/nee]: ").strip().lower()
    return invoer in ("ja", "j", "yes", "y")


def stuur_calendar_uitnodiging(
    rapport_doc_id: str,
    slides_id: str,
    norm: str,
    deelnemers: list[str] | None = None,
    audit_datum: str | None = None,
    calendar_id: str | None = None,
) -> str | None:
    """Maak een Google Calendar-uitnodiging aan via `gws` CLI.

    Retourneert het event-ID of `None` als overgeslagen (geen deelnemers
    of bevestiging geweigerd).
    """
    calendar_id = calendar_id or os.environ.get("AUDIT_CALENDAR_ID", "primary")
    deelnemers = deelnemers or []
    if not deelnemers:
        logger.info("Calendar-uitnodiging overgeslagen: geen deelnemers geconfigureerd")
        return None

    if not _bevestig("Google Calendar uitnodiging versturen", deelnemers):
        logger.info("Calendar-uitnodiging geannuleerd door gebruiker.")
        return None

    if audit_datum:
        start_dt = datetime.fromisoformat(audit_datum)
    else:
        start_dt = datetime.combine(date.today(), datetime.min.time().replace(hour=9))
    eind_dt = start_dt + timedelta(hours=2)

    norm_labels = {
        "9001": "ISO 9001:2015",
        "27001": "ISO 27001:2022",
        "beide": "ISO 9001:2015 + ISO 27001:2022",
    }
    norm_label = norm_labels.get(norm, norm)

    beschrijving = (
        f"Bespreking auditresultaten {norm_label}\n\n"
        f"Auditrapport: https://docs.google.com/document/d/{rapport_doc_id}\n"
        f"Presentatie: https://docs.google.com/presentation/d/{slides_id}\n\n"
        f"Aangemaakt door geautomatiseerd audit-systeem."
    )

    cmd: list[str] = [
        "gws",
        "calendar",
        "+insert",
        "--calendar",
        calendar_id,
        "--summary",
        f"Interne audit {norm_label} — bevindingspresentatie",
        "--start",
        start_dt.strftime("%Y-%m-%dT%H:%M:%S+02:00"),
        "--end",
        eind_dt.strftime("%Y-%m-%dT%H:%M:%S+02:00"),
        "--description",
        beschrijving,
    ]
    for deelnemer in deelnemers:
        cmd += ["--attendee", deelnemer]

    # `cmd` is een vaste lijst die met module-geconfigureerde gws-CLI begint en
    # waarden uit env/args bevat — geen shell-injectie mogelijk. Auditor heeft
    # bovendien expliciet bevestigd (zie _bevestig hierboven).
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)  # nosec B603 B607
    event: dict[str, Any] = json.loads(result.stdout)
    event_id: str = event.get("id", "")
    logger.info("Calendar-uitnodiging aangemaakt: %s", event_id)
    return event_id


def stuur_gmail_notificatie(
    rapport_doc_id: str,
    slides_id: str,
    norm: str,
    bevindingen: list[dict[str, Any]],
    ontvangers: list[str] | None = None,
) -> bool:
    """Verstuur Gmail-notificatie via `gws` CLI.

    Retourneert `True` als verstuurd, `False` als overgeslagen.
    """
    ontvangers_env = os.environ.get("AUDIT_NOTIFICATIE_ONTVANGERS", "")
    if ontvangers is None:
        ontvangers = [o.strip() for o in ontvangers_env.split(",") if o.strip()]

    if not ontvangers:
        logger.info("Gmail-notificatie overgeslagen: geen ontvangers geconfigureerd")
        return False

    if not _bevestig("Gmail-notificatie versturen", ontvangers):
        logger.info("Gmail-notificatie geannuleerd door gebruiker.")
        return False

    nc_count = sum(1 for b in bevindingen if b.get("classificatie") == "NC")
    ofi_count = sum(1 for b in bevindingen if b.get("classificatie") == "OFI")
    norm_labels = {
        "9001": "ISO 9001:2015",
        "27001": "ISO 27001:2022",
        "beide": "ISO 9001:2015 + ISO 27001:2022",
    }
    norm_label = norm_labels.get(norm, norm)

    onderwerp = f"Auditrapport {norm_label} — {date.today()}"
    tekst = (
        "Beste collega,\n\n"
        f"Het auditrapport voor {norm_label} is gereed.\n\n"
        "Samenvatting resultaten:\n"
        f"  Non-conformiteiten (NC): {nc_count}\n"
        f"  Kansen voor verbetering (OFI): {ofi_count}\n\n"
        "Documenten:\n"
        f"  Auditrapport: https://docs.google.com/document/d/{rapport_doc_id}\n"
        f"  Presentatie:  https://docs.google.com/presentation/d/{slides_id}\n\n"
        "Met vriendelijke groet,\n"
        "Geautomatiseerd Audit Systeem\n"
        f"Datum: {date.today()}"
    )

    for ontvanger in ontvangers:
        # Idem als calendar-call: vaste arglist, gws-CLI, auditor-bevestigd.
        subprocess.run(  # nosec B603 B607
            [
                "gws",
                "gmail",
                "+send",
                "--to",
                ontvanger,
                "--subject",
                onderwerp,
                "--body",
                tekst,
            ],
            check=True,
            capture_output=True,
        )
        logger.info("E-mail verstuurd naar: %s", ontvanger)

    return True
