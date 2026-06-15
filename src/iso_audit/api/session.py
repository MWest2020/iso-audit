"""Auditsessie-state: findings.json + append-only triage-log.

Een sessie is een working-directory met ``findings.json`` (de run-output) en een
``triage_log.jsonl`` (append-only auditor-beslissingen). De render gebeurt via
de bestaande motor (`build_memo`/renderer). Append-only is de auditeerbaarheids-
garantie: reclassificatie/triage wordt nooit overschreven, alleen toegevoegd.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import yaml

from iso_audit.memo.builder import build_memo
from iso_audit.memo.models import Finding, MemoInput, Severity, TriageStatus
from iso_audit.memo.norm_lookup import laad_norm_db
from iso_audit.memo.renderer.html import MemoRendererImpl
from iso_audit.memo.theme.profile import Profile, laad_profiel


class SessionError(ValueError):
    """Sessie kon niet geladen worden of een actie is ongeldig."""


class AuditSession:
    """Bestand-gebaseerde auditsessie (reproduceerbaar, hervatbaar)."""

    def __init__(
        self,
        session_dir: str | Path,
        *,
        profile: str,
        norms_dir: str | Path,
        memo_input_path: str | Path,
    ) -> None:
        self.dir = Path(session_dir)
        self.findings_path = self.dir / "findings.json"
        self.triage_log = self.dir / "triage_log.jsonl"
        if not self.findings_path.is_file():
            raise SessionError(f"Geen findings.json in sessie-dir: {self.dir}")
        self._profile_ref = profile
        self._norms_dir = norms_dir
        self._memo_input_path = Path(memo_input_path)

    # --- findings + triage ---------------------------------------------------

    def findings(self) -> list[Finding]:
        data = json.loads(self.findings_path.read_text(encoding="utf-8"))
        return [Finding(**item) for item in data]

    def _save(self, findings: list[Finding]) -> None:
        self.findings_path.write_text(
            json.dumps([f.model_dump() for f in findings], ensure_ascii=False, indent=1),
            encoding="utf-8",
        )

    def _log(self, entries: list[dict[str, str]]) -> None:
        with self.triage_log.open("a", encoding="utf-8") as fh:
            for e in entries:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")

    def apply_triage(
        self,
        finding_id: str,
        *,
        severity: Severity | None = None,
        triage_status: TriageStatus | None = None,
        reason: str,
        actor: str = "auditor",
        now: datetime | None = None,
    ) -> Finding:
        """Reclassificeer/triage één finding; legt de override append-only vast."""
        findings = self.findings()
        doel = next((f for f in findings if f.id == finding_id), None)
        if doel is None:
            raise SessionError(f"Finding {finding_id!r} niet gevonden.")
        stamp = (now or datetime.now(UTC)).strftime("%Y-%m-%dT%H:%M:%SZ")
        wijzigingen: list[tuple[str, str, str]] = []
        if severity is not None and severity != doel.severity:
            wijzigingen.append(("severity", doel.severity, severity))
            doel.severity = severity
        if triage_status is not None and triage_status != doel.triage_status:
            wijzigingen.append(("triage_status", doel.triage_status, triage_status))
            doel.triage_status = triage_status
        if not wijzigingen:
            return doel
        self._save(findings)
        self._log(
            [
                {
                    "timestamp": stamp,
                    "actor": actor,
                    "finding_id": finding_id,
                    "field": veld,
                    "from": oud,
                    "to": nieuw,
                    "reason": reason,
                }
                for veld, oud, nieuw in wijzigingen
            ]
        )
        return doel

    def trail(self) -> list[dict[str, str]]:
        """De append-only triage-trail (chronologisch)."""
        if not self.triage_log.is_file():
            return []
        return [
            json.loads(regel)
            for regel in self.triage_log.read_text(encoding="utf-8").splitlines()
            if regel.strip()
        ]

    # --- render --------------------------------------------------------------

    def _profile(self) -> Profile:
        return laad_profiel(self._profile_ref)

    def render_html(self) -> str:
        mi = MemoInput(**(yaml.safe_load(self._memo_input_path.read_text("utf-8")) or {}))
        memo = build_memo(
            findings=self.findings(),
            historical_ncs=[],
            profile=self._profile(),
            norm_db=laad_norm_db(self._norms_dir),
            memo_input=mi,
        )
        return MemoRendererImpl().render_html(memo, self._profile())

    def export_pdf(self, output: str | Path) -> Path:
        pad = Path(output)
        MemoRendererImpl().render_pdf(self.render_html(), pad)
        return pad
