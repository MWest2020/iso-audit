"""`SlackNotifier` — handoff via Slack incoming webhooks of Web API (§3.2.2).

Hangt aan een Slack-channel via:

- `SLACK_WEBHOOK_URL` (eenvoudig, geen OAuth, geen button-actions),
- of `SLACK_BOT_TOKEN` + `SLACK_CHANNEL_ID` (Web API, ondersteunt
  Block Kit + interactive actions in een latere fase).

In deze eerste implementatie sturen we Block-Kit-style berichten met de
decision-velden + een korte instructie. Button-callbacks (Slack Events
API → `DecisionResolver.resolve`) komen in §3.2.3 — voor MVP reageert
de auditor handmatig door de pipeline-CLI te draaien of via de
Email-portaal-route.

De `vraag_besluit`-call retourneert `str(decisions.id)` als correlatie-
sleutel; de :class:`iso_audit.notifiers.resolver.SqliteDecisionResolver`
gebruikt diezelfde id om de respons terug te koppelen.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import requests

from iso_audit.modes.base import Decision
from iso_audit.notifiers import register

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT_S = 10.0


@register
class SlackNotifier:
    """Notifier die `Decision`s naar Slack post via webhook of Web API."""

    naam: str = "slack"

    def __init__(
        self,
        webhook_url: str | None = None,
        bot_token: str | None = None,
        channel_id: str | None = None,
        timeout_s: float = _DEFAULT_TIMEOUT_S,
    ) -> None:
        """Construct met expliciete creds of fallback naar env-vars.

        Een van de twee paden moet werken:

        - `webhook_url` (of `SLACK_WEBHOOK_URL`): één-richtings, geen
          button-actions in MVP.
        - `bot_token` + `channel_id` (of `SLACK_BOT_TOKEN`/`SLACK_CHANNEL_ID`):
          Web API, biedt later interactive actions.

        Bij gebrek aan beide paden: :class:`OSError` bij `vraag_besluit`.
        """
        self._webhook_url = webhook_url or os.environ.get("SLACK_WEBHOOK_URL", "")
        self._bot_token = bot_token or os.environ.get("SLACK_BOT_TOKEN", "")
        self._channel_id = channel_id or os.environ.get("SLACK_CHANNEL_ID", "")
        self._timeout_s = timeout_s

    def vraag_besluit(self, decision: Decision) -> str:
        """Stuur Slack-bericht en retourneer een `decision_id`-correlatie-string.

        De `decision_id` moet hier al door :class:`IntegerMode` toegekend
        zijn — IntegerMode injecteert hem via `decision.context["decision_id"]`.
        Dit is een tijdelijke shape tot §3.2.3 (Slack Events) is gebouwd;
        daar wordt de id uit Slack's `private_metadata` gelezen.
        """
        decision_id = str(decision.context.get("decision_id", ""))
        if not decision_id:
            raise ValueError(
                "Slack notifier verwacht `decision_id` in decision.context "
                "(door IntegerMode geïnjecteerd)"
            )

        payload = _build_payload(decision, decision_id)

        if self._bot_token and self._channel_id:
            self._post_via_web_api(payload)
        elif self._webhook_url:
            self._post_via_webhook(payload)
        else:
            raise OSError(
                "Geen Slack-creds: zet SLACK_WEBHOOK_URL of SLACK_BOT_TOKEN + SLACK_CHANNEL_ID"
            )
        return decision_id

    def healthcheck(self) -> dict[str, object]:
        """Status + welk auth-pad actief is."""
        if self._bot_token and self._channel_id:
            return {"status": "ok", "naam": self.naam, "auth": "bot-token"}
        if self._webhook_url:
            return {"status": "ok", "naam": self.naam, "auth": "webhook"}
        return {
            "status": "fail",
            "naam": self.naam,
            "reden": "geen SLACK_WEBHOOK_URL of SLACK_BOT_TOKEN",
        }

    def _post_via_webhook(self, payload: dict[str, Any]) -> None:
        resp = requests.post(
            self._webhook_url,
            json=payload,
            timeout=self._timeout_s,
        )
        if not resp.ok:
            raise OSError(f"Slack webhook gaf {resp.status_code}: {resp.text[:200]}")

    def _post_via_web_api(self, payload: dict[str, Any]) -> None:
        body = {"channel": self._channel_id, **payload}
        resp = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": f"Bearer {self._bot_token}",
                "Content-Type": "application/json; charset=utf-8",
            },
            json=body,
            timeout=self._timeout_s,
        )
        data = resp.json()
        if not data.get("ok", False):
            raise OSError(f"Slack Web API gaf error: {data.get('error', 'onbekend')}")


def _build_payload(decision: Decision, decision_id: str) -> dict[str, Any]:
    """Bouw een Block-Kit message-payload voor één Decision."""
    risico_emoji = {
        "hoog": ":rotating_light:",
        "midden": ":warning:",
        "laag": ":information_source:",
    }
    emoji = risico_emoji.get(decision.risico, ":question:")
    context_snippet = json.dumps(dict(decision.context), indent=2, ensure_ascii=False)
    voorstel_snippet = json.dumps(dict(decision.voorstel), indent=2, ensure_ascii=False)
    text = (
        f"{emoji} *iso-audit beslissing #{decision_id}*\n"
        f"*Punt:* `{decision.punt}` (risico: {decision.risico})\n"
        f"*Voorstel:* ```{voorstel_snippet}```\n"
        f"*Context:* ```{context_snippet}```"
    )
    return {
        "text": f"iso-audit beslissing #{decision_id} ({decision.punt})",
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": (
                            f"audit_id: `{decision.audit_id}` · "
                            "Reageer via interactive buttons (§3.2.3) "
                            "of `iso-audit decision resolve` CLI."
                        ),
                    }
                ],
            },
        ],
    }
