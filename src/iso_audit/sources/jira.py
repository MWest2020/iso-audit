"""`JiraSource` — Jira Cloud REST API v3 adapter (§3.4.1-3).

Read-only: enumereert Jira issues als `Document`s en kan ze ook als
`Finding`s exposeren (voor backlog-items die direct compliance-bewijs
zijn — bv. een ISO-aanbevelings-ticket).

Auth: persoonlijke Atlassian API-token via env-vars (`JIRA_BASE_URL`,
`JIRA_USER_EMAIL` — `JIRA_EMAIL` als fallback —, `JIRA_API_TOKEN`) met HTTP
basic auth (Atlassian's standaard voor Cloud-token-auth). JQL-config via
`JIRA_JQL` (leeg = geen filter). Scope op project(en) via `JIRA_PROJECTS`
(komma-gescheiden, bv. "ISO"): wordt als `project in (…)` AND-prefix op elke
query gezet zodat een run binnen de ISO-scope blijft.

Pagination: Jira Cloud's `/search` endpoint geeft maximaal `maxResults=100`
per call; deze adapter paginate via `startAt` tot uitputting.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from typing import Any

import requests

from iso_audit.sources import register
from iso_audit.sources.base import Document, Finding

logger = logging.getLogger(__name__)

_DEFAULT_PAGE_SIZE = 100
_DEFAULT_TIMEOUT_S = 30.0


@register
class JiraSource:
    """Source-adapter voor Jira Cloud issues."""

    naam: str = "jira"

    def __init__(
        self,
        base_url: str | None = None,
        email: str | None = None,
        api_token: str | None = None,
        default_jql: str | None = None,
        page_size: int = _DEFAULT_PAGE_SIZE,
        timeout_s: float = _DEFAULT_TIMEOUT_S,
    ) -> None:
        """Construct met expliciete creds of fallback naar env-vars."""
        self._base_url = (base_url or os.environ.get("JIRA_BASE_URL", "")).rstrip("/")
        # JIRA_USER_EMAIL is de gekozen naam; JIRA_EMAIL blijft als fallback voor
        # bestaande configs (boring & auditable: geen stille breaking change).
        self._email = email or os.environ.get("JIRA_USER_EMAIL") or os.environ.get("JIRA_EMAIL", "")
        self._api_token = api_token or os.environ.get("JIRA_API_TOKEN", "")
        self._jql = default_jql or os.environ.get("JIRA_JQL", "")
        # Scope-filter op project(en) — immutable runtime-conf. Komma-gescheiden,
        # bv. JIRA_PROJECTS="ISO" of "ISO,COMP". Wordt als AND-prefix op elke
        # effectieve JQL gezet (documenten én findings).
        self._projects = [
            p.strip() for p in os.environ.get("JIRA_PROJECTS", "").split(",") if p.strip()
        ]
        self._page_size = page_size
        self._timeout_s = timeout_s

    def _scope_jql(self, base_jql: str) -> str:
        """Beperk een JQL tot de geconfigureerde projecten (`JIRA_PROJECTS`).

        Geen projecten geconfigureerd → JQL blijft ongewijzigd. Anders wordt
        `project in ("ISO", …)` als AND-conditie voorgevoegd, zodat een run
        binnen de ISO-scope blijft, ongeacht de onderliggende query.
        """
        if not self._projects:
            return base_jql
        quoted = ", ".join(f'"{p}"' for p in self._projects)
        scope = f"project in ({quoted})"
        return f"({scope}) AND ({base_jql})" if base_jql.strip() else scope

    def list_documents(self, filter: dict[str, object] | None = None) -> Iterator[Document]:
        """Iterate over Jira issues; elke issue wordt een `Document`.

        `filter` mag een `{"jql": "..."}`-veld bevatten om de default JQL te
        overschrijven. Andere keys worden genegeerd (read-only contract).
        """
        jql = ""
        if filter and isinstance(filter.get("jql"), str):
            jql = str(filter["jql"])
        elif self._jql:
            jql = self._jql

        for issue in self._iterate_issues(self._scope_jql(jql)):
            yield _issue_to_document(issue)

    def fetch_content(self, doc: Document) -> str:
        """Haal de volledige tekstuele inhoud van één issue op.

        Jira's `description` is in Atlassian Document Format (ADF). Voor MVP
        retourneren we een platte-tekst-rendering van `description` + de
        comments. Rich-content rendering komt mee met §3.4.6 docs of bij
        eerste integer-run als het nodig blijkt.
        """
        url = f"{self._base_url}/rest/api/3/issue/{doc.id}"
        resp = self._http_get(url, params={"fields": "description,comment"})
        data = resp.json()
        return _render_issue_inhoud(data)

    def list_findings(self, sessie_id: str) -> Iterator[Finding]:
        """Issues met een ISO-label of `compliance`-label worden als Finding gemodelleerd.

        `sessie_id` correspondeert aan de audit-run; we voegen het toe als
        prefix aan finding.id zodat dezelfde issue in verschillende runs
        verschillende Finding-id's krijgt.

        Filter via JQL: `labels in (iso27001, iso9001, compliance) AND
        statusCategory != Done`. Override mogelijk via env-var
        `JIRA_FINDINGS_JQL`.
        """
        findings_jql = os.environ.get(
            "JIRA_FINDINGS_JQL",
            "labels in (iso27001, iso9001, compliance) AND statusCategory != Done",
        )
        for issue in self._iterate_issues(self._scope_jql(findings_jql)):
            yield _issue_to_finding(issue, sessie_id)

    def healthcheck(self) -> dict[str, object]:
        """Status + tenant (`base_url`) en config-staat."""
        if not self._base_url or not self._email or not self._api_token:
            return {
                "status": "fail",
                "naam": self.naam,
                "reden": "JIRA_BASE_URL / JIRA_USER_EMAIL / JIRA_API_TOKEN ontbreken",
            }
        try:
            resp = self._http_get(f"{self._base_url}/rest/api/3/myself")
            user = resp.json()
            return {
                "status": "ok",
                "naam": self.naam,
                "tenant": self._base_url,
                "user": user.get("displayName", ""),
            }
        except Exception as e:
            return {
                "status": "fail",
                "naam": self.naam,
                "reden": str(e),
            }

    def _iterate_issues(self, jql: str) -> Iterator[dict[str, Any]]:
        """Paginated iterator over Jira search-API."""
        if not self._base_url:
            return
        url = f"{self._base_url}/rest/api/3/search"
        start_at = 0
        while True:
            resp = self._http_get(
                url,
                params={
                    "jql": jql,
                    "startAt": start_at,
                    "maxResults": self._page_size,
                    "fields": "summary,status,labels,updated,description",
                },
            )
            data = resp.json()
            issues: list[dict[str, Any]] = data.get("issues", [])
            yield from issues
            total = int(data.get("total", 0))
            start_at += len(issues)
            if not issues or start_at >= total:
                break

    def _http_get(self, url: str, params: dict[str, object] | None = None) -> requests.Response:
        # requests accepts a mapping; cast for mypy precision.
        resp = requests.get(
            url,
            params=params or {},  # type: ignore[arg-type]
            auth=(self._email, self._api_token),
            headers={"Accept": "application/json"},
            timeout=self._timeout_s,
        )
        if not resp.ok:
            raise OSError(f"Jira API {resp.status_code} op {url}: {resp.text[:200]}")
        return resp


def _issue_to_document(issue: dict[str, Any]) -> Document:
    """Map Jira-issue-JSON naar `Document`."""
    fields = issue.get("fields", {})
    return Document(
        id=str(issue.get("key", "")),
        titel=str(fields.get("summary", "")),
        bron="jira",
        type="issue",
        laatst_gewijzigd=str(fields.get("updated", "")),
        inhoud_uri=f"jira://{issue.get('key', '')}",
    )


def _issue_to_finding(issue: dict[str, Any], sessie_id: str) -> Finding:
    """Map Jira-issue naar `Finding`. Labels worden clausule-id's."""
    fields = issue.get("fields", {})
    labels: list[str] = list(fields.get("labels", []) or [])
    clausule_ids = [_label_naar_clausule(label) for label in labels]
    clausule_ids = [c for c in clausule_ids if c]
    return Finding(
        id=f"{sessie_id}:{issue.get('key', '')}",
        bron="jira",
        clausule_ids=clausule_ids,
        omschrijving=str(fields.get("summary", "")),
        bewijs_uris=[f"jira://{issue.get('key', '')}"],
    )


def _label_naar_clausule(label: str) -> str:
    """Heuristische map van Jira-label naar clausule-id.

    Voor MVP geven we 'iso27001' / 'iso9001' / 'compliance' direct terug;
    een fijnere map (e.g. `iso27001-5.11` → `5.11`) kan in een
    pipeline-extension worden toegevoegd.
    """
    prefix = "iso27001-"
    if label.startswith(prefix):
        return label[len(prefix) :]
    prefix2 = "iso9001-"
    if label.startswith(prefix2):
        return label[len(prefix2) :]
    return ""


def _render_issue_inhoud(data: dict[str, Any]) -> str:
    """Maak een platte-tekst-rendering van een Jira issue."""
    fields = data.get("fields", {})
    parts: list[str] = []
    desc = fields.get("description")
    if isinstance(desc, dict):
        parts.append(_render_adf(desc))
    elif isinstance(desc, str):
        parts.append(desc)
    comments = (
        fields.get("comment", {}).get("comments", [])
        if isinstance(fields.get("comment"), dict)
        else []
    )
    for comment in comments:
        body = comment.get("body")
        if isinstance(body, dict):
            parts.append("\n---\n" + _render_adf(body))
        elif isinstance(body, str):
            parts.append("\n---\n" + body)
    return "\n".join(parts).strip()


def _render_adf(node: dict[str, Any]) -> str:
    """Minimale Atlassian Document Format → plain text."""
    parts: list[str] = []
    text = node.get("text")
    if isinstance(text, str):
        parts.append(text)
    for child in node.get("content", []) or []:
        if isinstance(child, dict):
            parts.append(_render_adf(child))
    if node.get("type") == "paragraph":
        parts.append("\n")
    return "".join(parts)
