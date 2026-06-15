"""Pydantic v2 models voor de auditmemo.

Splitst input-modellen (Finding, HistoricalNC) van de samengestelde
render-modellen (NCBlock, ImprovementBlock, AuditMemo). Boring & auditable:
strikte velden, geen impliciete defaults waar een keuze betekenis heeft.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Severity = Literal["NC", "OFI", "POSITIVE", "UNCLASSIFIED"]
HistoricalStatus = Literal["open", "in_progress", "closed"]


# --- Input-modellen ---------------------------------------------------------


class Finding(BaseModel):
    """Eén bevinding uit de findings-dataset (input-contract)."""

    id: str
    severity: Severity
    standard: str  # norm-DB slug, bv. "iso-27001-2022"
    clause: str  # primaire clausule, bv. "10.2"
    title: str
    description: str
    evidence: list[str] = Field(default_factory=list)
    extra_clauses: list[str] = Field(default_factory=list)  # extra geciteerde clausules
    source_memo: str | None = None
    promote_to_improvement: bool = False


class HistoricalNC(BaseModel):
    """Entry uit het doorlopende historical-NCs-register."""

    id: str
    source_audit: str
    source_document: str
    finding_summary: str
    status: HistoricalStatus
    closed_date: str | None = None
    closed_evidence: str | None = None


# --- Render-modellen (samengesteld) -----------------------------------------


class ClauseCitation(BaseModel):
    """Genormeerd citaat zoals het in een NC/verbeterpunt-blok verschijnt."""

    standard: str
    clause: str
    title: str
    text: str


class ActionRow(BaseModel):
    """Rij in een action-table. Lege wie/waar/uiterlijk = placeholder."""

    wat: str
    wie: str | None = None
    waar: str | None = None
    uiterlijk: str | None = None


class NCBlock(BaseModel):
    """Eén NC-blok: kan meerdere clausules citeren en meerdere evidence-items bundelen."""

    title: str
    citations: list[ClauseCitation]
    deviation: str  # "waar de praktijk afwijkt"
    pattern_note: str | None = None  # cross-clause patroon (auto)
    corrective_measure: str  # dwingende taal, geen "aanbeveling"
    actions: list[ActionRow] = Field(default_factory=list)


class ImprovementBlock(BaseModel):
    """Verbeterpunt met verplichte classificatie-rationale."""

    title: str
    citations: list[ClauseCitation]
    deviation: str
    classification_rationale: str  # "waarom verbeterpunt en geen NC?"
    suggestion: str | None = None


class MemoContext(BaseModel):
    """Context-sectie: data-gedreven, niet hardcoded."""

    audit_cycle: str
    scope: dict[str, str]  # norm-slug -> geauditeerde hoofdstukken
    sources: list[str]
    dataset_counts: dict[str, int]  # totaal + per severity
    scope_caveat: str
    independence_caveat: str | None = None
    discussion: str | None = None  # datum + met wie; None = placeholder


class AuditMemo(BaseModel):
    """Top-level render-model: alles wat de template nodig heeft."""

    title: str
    subtitle: str  # auditor | rol · cyclus
    date: str
    version: str
    lead_summary: str
    context: MemoContext
    nc_blocks: list[NCBlock]
    improvements: list[ImprovementBlock]
    historical_ncs: list[HistoricalNC]
    detail_report_ref: str
