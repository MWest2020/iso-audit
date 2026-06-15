"""`EmailNotifier` — handoff via SMTP + magic-link respons (§3.2.5).

MVP-implementatie: stuurt een mail met de decision-velden + vier magic-links
(`?action=approve|reject|modify|abort`) naar een lokaal Flask-portaal
(§3.2.6 — wordt in eigen module geïmplementeerd). Het portaal valideert het
single-use token en roept :class:`SqliteDecisionResolver.resolve` aan.

Deze module schrijft GEEN tokens naar disk — dat is verantwoordelijkheid
van het portaal (`portal.py`). De notifier genereert wel een random token
per Decision en zet hem in de magic-link URL.

Auth: SMTP via env-vars (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`,
`SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_TLS`). Ontvanger via
`AUDIT_NOTIFIER_EMAIL` of `to_address`-arg.

Acceptable-risk-notitie: het portaal draait in MVP zonder TLS. Mark heeft
expliciet ingestemd. Zie `docs/notifiers/email.md` (§3.2.11).
"""

from __future__ import annotations

import logging
import os
import secrets
import smtplib
from email.message import EmailMessage

from iso_audit.modes.base import Decision
from iso_audit.notifiers import register

logger = logging.getLogger(__name__)

_DEFAULT_PORTAL_URL = "http://localhost:8765"


@register
class EmailNotifier:
    """Notifier die `Decision`s mailt + magic-link genereert naar portaal."""

    naam: str = "email"

    def __init__(
        self,
        to_address: str | None = None,
        portal_url: str | None = None,
        smtp_host: str | None = None,
        smtp_port: int | None = None,
        smtp_user: str | None = None,
        smtp_password: str | None = None,
        smtp_from: str | None = None,
        smtp_tls: bool | None = None,
    ) -> None:
        """Construct met expliciete config of fallback naar env-vars."""
        self._to = to_address or os.environ.get("AUDIT_NOTIFIER_EMAIL", "")
        self._portal_url = portal_url or os.environ.get("ISO_AUDIT_PORTAL_URL", _DEFAULT_PORTAL_URL)
        self._host = smtp_host or os.environ.get("SMTP_HOST", "")
        self._port = smtp_port or int(os.environ.get("SMTP_PORT", "587"))
        self._user = smtp_user or os.environ.get("SMTP_USER", "")
        self._password = smtp_password or os.environ.get("SMTP_PASSWORD", "")
        self._from = smtp_from or os.environ.get("SMTP_FROM", "")
        self._tls = (
            smtp_tls
            if smtp_tls is not None
            else os.environ.get("SMTP_TLS", "true").lower() == "true"
        )

    def vraag_besluit(self, decision: Decision) -> str:
        """Verstuur de magic-link-mail; retourneer het `decision_id`."""
        decision_id = str(decision.context.get("decision_id", ""))
        if not decision_id:
            raise ValueError(
                "Email notifier verwacht `decision_id` in decision.context "
                "(door IntegerMode geïnjecteerd)"
            )
        if not self._to or not self._host or not self._from:
            raise OSError(
                "Email notifier mist config: AUDIT_NOTIFIER_EMAIL, "
                "SMTP_HOST, SMTP_FROM zijn verplicht"
            )

        token = secrets.token_urlsafe(32)
        msg = _build_message(
            decision=decision,
            decision_id=decision_id,
            token=token,
            portal_url=self._portal_url,
            from_addr=self._from,
            to_addr=self._to,
        )
        self._send(msg)
        # Token-persistentie ligt bij het portaal (§3.2.6). De decision_id is
        # genoeg correlatie voor de mode-polling-laag.
        logger.info("Email verstuurd voor decision %s naar %s", decision_id, self._to)
        return decision_id

    def healthcheck(self) -> dict[str, object]:
        ontbrekend = [
            naam
            for naam, waarde in [
                ("to_address", self._to),
                ("smtp_host", self._host),
                ("smtp_from", self._from),
            ]
            if not waarde
        ]
        if ontbrekend:
            return {
                "status": "fail",
                "naam": self.naam,
                "reden": f"ontbrekende config: {ontbrekend}",
            }
        return {
            "status": "ok",
            "naam": self.naam,
            "smtp_host": self._host,
            "tls": self._tls,
        }

    def _send(self, msg: EmailMessage) -> None:
        if self._tls:
            with smtplib.SMTP(self._host, self._port) as smtp:
                smtp.starttls()
                if self._user:
                    smtp.login(self._user, self._password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(self._host, self._port) as smtp:
                if self._user:
                    smtp.login(self._user, self._password)
                smtp.send_message(msg)


def _build_message(
    decision: Decision,
    decision_id: str,
    token: str,
    portal_url: str,
    from_addr: str,
    to_addr: str,
) -> EmailMessage:
    """Bouw de SMTP-message met vier magic-link knoppen."""
    base = f"{portal_url}/decision/{decision_id}"
    qs = f"?token={token}"
    links = {
        "Goedkeuren": f"{base}/approve{qs}",
        "Afwijzen": f"{base}/reject{qs}",
        "Aanpassen": f"{base}/modify{qs}",
        "Afbreken": f"{base}/abort{qs}",
    }
    body = _format_body(decision, decision_id, links)

    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = f"[iso-audit] Beslissing #{decision_id} — {decision.punt}"
    msg.set_content(body)
    return msg


def _format_body(
    decision: Decision,
    decision_id: str,
    links: dict[str, str],
) -> str:
    import json

    voorstel = json.dumps(dict(decision.voorstel), indent=2, ensure_ascii=False)
    context = json.dumps(dict(decision.context), indent=2, ensure_ascii=False)
    links_text = "\n".join(f"- {naam}: {url}" for naam, url in links.items())
    return (
        f"iso-audit vraagt een besluit.\n\n"
        f"Decision #{decision_id}\n"
        f"Punt:   {decision.punt}\n"
        f"Risico: {decision.risico}\n"
        f"Audit:  {decision.audit_id}\n\n"
        f"Voorstel:\n{voorstel}\n\n"
        f"Context:\n{context}\n\n"
        f"Reageer via een van deze links (single-use, TTL via portaal):\n"
        f"{links_text}\n\n"
        f"Bij 'Aanpassen' opent een formulier waar je het besluit kunt "
        f"bewerken voor je het indient.\n"
    )


def _gegenereerde_token_lengte(token: str) -> int:  # pragma: no cover
    """Helper voor tests/docs — toont de URL-safe token-lengte."""
    return len(token)


# Token-opslag-architectuur: zie `docs/notifiers/email.md` (§3.2.11). Het
# portaal (`portal.py`, §3.2.6) houdt de tokens; de notifier raakt ze
# alleen aan om ze in de URL te embedden. Single-use validatie en TTL
# leven in het portaal.
