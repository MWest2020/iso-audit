"""LLM-draft van management-NC's uit een ruwe findings-dataset (optie A).

Clustert de NC-findings per clausule, laat de LLM per top-cluster één
management-NC draften (titel + afwijking-narratief + corrigerende maatregel) en
levert een **draft findings-lijst** die de auditor reviewt/redigeert vóór de
render. Auditor-spiegel: de tool draaft, de mens beslist. Temp 0 → reproduceerbaar.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import anthropic

from iso_audit.memo.models import ActionRow, Finding
from iso_audit.memo.norm_lookup import NormDatabase

CLAUDE_MODEL = "claude-haiku-4-5-20251001"
_PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


def _laad_prompt(naam: str, vervangingen: dict[str, str]) -> str:
    tekst = (_PROMPT_DIR / f"{naam}.md").read_text(encoding="utf-8")
    tekst = re.sub(r"<!--.*?-->\n?", "", tekst, flags=re.DOTALL)
    for sleutel, waarde in vervangingen.items():
        tekst = tekst.replace(f"{{{{{sleutel}}}}}", waarde)
    return tekst.strip()


def _parse_json(tekst: str) -> dict[str, Any]:
    """Pak het JSON-object uit een LLM-antwoord (eventueel in ```-fences)."""
    schoon = re.sub(r"^```(?:json)?|```$", "", tekst.strip(), flags=re.MULTILINE).strip()
    match = re.search(r"\{.*\}", schoon, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Geen JSON in LLM-antwoord: {tekst[:120]!r}")
    data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("LLM-antwoord is geen JSON-object.")
    return data


def cluster_ncs(findings: list[Finding], top_n: int) -> list[list[Finding]]:
    """Groepeer NC-findings per clausule; geef de ``top_n`` grootste clusters."""
    per_clausule: dict[str, list[Finding]] = defaultdict(list)
    for f in findings:
        if f.severity == "NC":
            per_clausule[f.clause].append(f)
    geordend = sorted(per_clausule.values(), key=lambda c: (-len(c), c[0].clause))
    return geordend[:top_n]


def _clausule_titel(norm_db: NormDatabase, standard: str, clause: str, language: str) -> str:
    try:
        return norm_db.citation(standard, clause, language).title
    except Exception:
        return clause


def _draft_cluster(
    cluster: list[Finding],
    norm_db: NormDatabase,
    language: str,
    client: anthropic.Anthropic,
) -> Finding:
    clause = cluster[0].clause
    standard = cluster[0].standard
    titel = _clausule_titel(norm_db, standard, clause, language)
    findings_blok = "\n".join(f"- {f.description[:200]}" for f in cluster)
    prompt = _laad_prompt(
        "nc_draft_v1",
        {
            "clausule": clause,
            "clausule_titel": titel,
            "aantal": str(len(cluster)),
            "findings_blok": findings_blok,
        },
    )
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=900,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    data = _parse_json(message.content[0].text)  # type: ignore[union-attr]
    extra = sorted({f.clause for f in cluster} - {clause})
    # Redenatie-lijst: wat de tool per bevinding aantrof — basis voor auditor-triage.
    reasoning = [f.description[:180] for f in cluster if f.description]
    return Finding(
        id=f"nc-{clause}",
        severity="NC",
        standard=standard,
        clause=clause,
        extra_clauses=extra,
        title=str(data.get("title") or f"NC clausule {clause}"),
        description=f"Gedistilleerd uit {len(cluster)} ruwe NC-bevindingen op clausule {clause}.",
        deviation=str(data.get("deviation") or ""),
        corrective_measure=str(data.get("corrective_measure") or ""),
        actions=[ActionRow(wat="(actie in te vullen door auditor)")],
        reasoning=reasoning,
        triage_status="open",
    )


def draft_findings(
    findings: list[Finding],
    *,
    norm_db: NormDatabase,
    language: str,
    top_n: int = 3,
    client: anthropic.Anthropic | None = None,
) -> list[Finding]:
    """Vervang de ruwe NC's door ``top_n`` LLM-gedrafte management-NC's.

    Niet-NC findings (OFI/positief) blijven behouden zodat pattern-detectie de
    juiste tellingen houdt. De auditor redigeert het resultaat vóór de render.
    """
    client = client or anthropic.Anthropic()
    clusters = cluster_ncs(findings, top_n)
    drafted = [_draft_cluster(cl, norm_db, language, client) for cl in clusters]
    overige = [f for f in findings if f.severity != "NC"]
    return drafted + overige
