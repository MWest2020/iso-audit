"""Auditsessie-state: findings.json + append-only triage-log.

Een sessie is een working-directory met ``findings.json`` (de run-output) en een
``triage_log.jsonl`` (append-only auditor-beslissingen). De render gebeurt via
de bestaande motor (`build_memo`/renderer). Append-only is de auditeerbaarheids-
garantie: reclassificatie/triage wordt nooit overschreven, alleen toegevoegd.
"""

from __future__ import annotations

import json
import re
import threading
import time
from dataclasses import dataclass, field
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


@dataclass
class _RunState:
    """Voortgang van de stap-2-run (indexatie/timer of live pipeline)."""

    status: str = "idle"
    total: int = 0
    done: int = 0
    start: float = 0.0
    pace: float = 0.0
    mode: str = "sim"
    log: list[str] = field(default_factory=list)


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
        self._run = _RunState()

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
        title: str | None = None,
        deviation: str | None = None,
        corrective_measure: str | None = None,
        reason: str,
        actor: str = "auditor",
        now: datetime | None = None,
    ) -> Finding:
        """Reclassificeer/triage/redigeer één finding; legt elke wijziging append-only vast."""
        findings = self.findings()
        doel = next((f for f in findings if f.id == finding_id), None)
        if doel is None:
            raise SessionError(f"Finding {finding_id!r} niet gevonden.")
        stamp = (now or datetime.now(UTC)).strftime("%Y-%m-%dT%H:%M:%SZ")
        wijzigingen: list[tuple[str, str, str]] = []

        def _maybe(veld: str, nieuw: str | None) -> None:
            if nieuw is None:
                return
            oud = getattr(doel, veld) or ""
            if nieuw != oud:
                wijzigingen.append((veld, str(oud)[:120], str(nieuw)[:120]))
                setattr(doel, veld, nieuw)

        _maybe("severity", severity)
        _maybe("triage_status", triage_status)
        _maybe("title", title)
        _maybe("deviation", deviation)
        _maybe("corrective_measure", corrective_measure)
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

    def counts(self) -> dict[str, int]:
        """Tel findings per severity."""
        telling: dict[str, int] = {}
        for f in self.findings():
            telling[f.severity] = telling.get(f.severity, 0) + 1
        return telling

    def config_options(self) -> dict[str, list[str]]:
        """Stap 1: keuzes voor de run — beschikbare normen (norm-DB) en bronnen."""
        from iso_audit.ingest import beschikbare_bronnen

        return {
            "norms": laad_norm_db(self._norms_dir).standards(),
            "sources": beschikbare_bronnen(),
        }

    def start_run(
        self,
        *,
        mode: str = "sim",
        norm: str = "9001",
        sources: list[str] | None = None,
        chapter: str | None = None,
        top_n: int = 0,
        pace_s: float = 0.05,
    ) -> dict[str, object]:
        """Stap 2: start de run. ``mode='live'`` = echte pipeline (Drive+LLM);
        ``mode='sim'`` = indexatie-timer (fallback). ``pace_s<=0`` = synchroon (tests).
        """
        if mode == "live":
            self._run = _RunState(status="running", total=7, start=time.monotonic(), mode="live")
            threading.Thread(
                target=self._run_live_worker,
                args=(norm, sources or ["drive"], chapter, top_n),
                daemon=True,
            ).start()
            return {"mode": "live", "status": "running"}

        total = len(self.findings())
        self._run = _RunState(
            status="running", total=total, start=time.monotonic(), pace=pace_s, mode="sim"
        )
        if pace_s <= 0:
            self._run.done = total
            self._run.status = "done"
        else:
            threading.Thread(target=self._run_worker, daemon=True).start()
        return {"mode": "sim", "total": total, "status": self._run.status}

    def _run_worker(self) -> None:
        run = self._run
        for i in range(run.total):
            time.sleep(run.pace)
            run.done = i + 1
        run.status = "done"

    def _run_live_worker(
        self, norm: str, sources: list[str], chapter: str | None, top_n: int
    ) -> None:
        from iso_audit.api.run_job import draft_from_db, run_live_pipeline

        def _on_log(msg: str) -> None:
            self._run.log.append(msg)
            m = re.search(r"Stap (\d+)/(\d+)", msg)
            if m:
                self._run.done, self._run.total = int(m.group(1)), int(m.group(2))

        try:
            run_live_pipeline(norm=norm, sources=sources, chapter=chapter, on_log=_on_log)
            self._run.log.append("Findings exporteren + kop-NC's draften…")
            drafted = draft_from_db(
                norm=norm, norms_dir=str(self._norms_dir), language="nl", top_n=top_n
            )
            self._save(drafted)
            self._run.done = self._run.total
            self._run.status = "done"
        except Exception as exc:  # surface elke pipeline-fout in de UI
            self._run.log.append(f"FOUT: {exc}")
            self._run.status = "error"

    def run_progress(self) -> dict[str, object]:
        """Voortgang van stap 2: done/total, verstreken tijd, ETA en (live) logregels."""
        r = self._run
        elapsed = (time.monotonic() - r.start) if r.status != "idle" else 0.0
        eta = (r.total - r.done) * (elapsed / r.done) if r.done and r.status == "running" else 0.0
        return {
            "status": r.status,
            "mode": r.mode,
            "total": r.total,
            "done": r.done,
            "elapsed_s": round(elapsed, 1),
            "eta_s": round(eta, 1),
            "log": r.log[-25:],
        }

    def run_summary(
        self, *, norms: list[str] | None = None, sources: list[str] | None = None
    ) -> dict[str, object]:
        """Stap 2: voer (of toon) de run o.b.v. de gekozen config."""
        return {
            "config": {"norms": norms or [], "sources": sources or []},
            "findings": len(self.findings()),
            "counts": self.counts(),
            "note": (
                "Findings uit de sessie (resultaat van een eerdere run). Live ingest "
                "via de gekozen bron(nen) is de connector-orchestration-fase."
            ),
        }

    def finding_context(self, finding_id: str) -> dict[str, object]:
        """Hover-context: de échte normtekst per clausule + waarom NC-kandidaat."""
        doel = next((f for f in self.findings() if f.id == finding_id), None)
        if doel is None:
            raise SessionError(f"Finding {finding_id!r} niet gevonden.")
        db = laad_norm_db(self._norms_dir)
        lang = self._profile().defaults.language
        citations: list[dict[str, str]] = []
        for clause in [doel.clause, *doel.extra_clauses]:
            try:
                citations.append(db.citation(doel.standard, clause, lang).model_dump())
            except Exception:  # ontbrekende clausule mag de hover niet breken
                continue
        return {
            "citations": citations,
            "reasoning": doel.reasoning,
            "deviation": doel.deviation or doel.description,
            "verify_with": doel.verify_with or "",
        }

    def conclusion(self) -> dict[str, object]:
        """Saturatie-conclusie na triage: telling + advies (auditor beslist)."""
        nc = [f for f in self.findings() if f.severity == "NC"]
        tally = {
            s: sum(1 for f in nc if f.triage_status == s)
            for s in ("open", "valide", "niet_valide", "follow_up")
        }
        open_n, follow = tally["open"], tally["follow_up"]
        if open_n:
            advies = f"{open_n} kandidaat-NC('s) nog niet beoordeeld."
        elif follow:
            advies = f"{follow} follow-up('s) open — meer audits nodig voor saturatie."
        else:
            advies = "Voldoende saturatie — de MT-memo kan opgesteld worden."
        return {
            "tally": tally,
            "all_triaged": open_n == 0,
            "saturated": open_n == 0 and follow == 0,
            "advice": advies,
        }

    def triage_summary(self) -> dict[str, object]:
        """Triage-voortgang: een memo mag pas bij 0 openstaande NC-kandidaten."""
        nc = [f for f in self.findings() if f.severity == "NC"]
        open_n = sum(1 for f in nc if f.triage_status == "open")
        return {"total_nc": len(nc), "open": open_n, "complete": open_n == 0}

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
