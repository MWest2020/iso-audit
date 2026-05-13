"""Snapshot-tests voor fixture-audit-2026-q1.

Twee niveaus:

1. **self-consistency** — verifieert dat `findings.csv` en
   `findings.expected.csv` intern consistent zijn (zelfde `doc_id`-set,
   zelfde antwoorden op `classificatie`/`clausule`/`norm`). Draait altijd
   en bewaakt dat de fixture als geheel niet uit elkaar loopt.

2. **classifier-output** — draait de gemigreerde classifier op
   `findings.csv` en vergelijkt tegen `findings.expected.csv`. Skipt
   automatisch tot `iso_audit.classification.findings` beschikbaar is
   (migratie in milestone B §2.2.5).
"""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).resolve().parent.parent.parent / "examples" / "fixture-audit-2026-q1"
FINDINGS_CSV = FIXTURE_DIR / "findings.csv"
EXPECTED_CSV = FIXTURE_DIR / "findings.expected.csv"


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


@pytest.mark.snapshot
def test_fixture_self_consistency() -> None:
    """`findings.expected.csv` moet exact de antwoord-velden uit `findings.csv` weerspiegelen."""
    findings = {r["doc_id"]: r for r in _load_csv(FINDINGS_CSV)}
    expected = {r["doc_id"]: r for r in _load_csv(EXPECTED_CSV)}

    assert findings, "findings.csv is leeg — fixture niet gegenereerd?"
    assert expected, "findings.expected.csv is leeg — fixture niet gegenereerd?"

    extra_in_findings = set(findings) - set(expected)
    extra_in_expected = set(expected) - set(findings)
    assert not extra_in_findings, f"doc_id's alleen in findings.csv: {sorted(extra_in_findings)}"
    assert not extra_in_expected, (
        f"doc_id's alleen in findings.expected.csv: {sorted(extra_in_expected)}"
    )

    mismatches: list[str] = []
    for doc_id, exp in expected.items():
        actual = findings[doc_id]
        for key in ("classificatie", "clausule", "norm"):
            if actual[key] != exp[key]:
                mismatches.append(f"{doc_id}.{key}: findings={actual[key]!r} expected={exp[key]!r}")
    assert not mismatches, "fixture self-consistency mismatches:\n" + "\n".join(mismatches)


@pytest.mark.snapshot
def test_fixture_selection_criteria() -> None:
    """Verifieer dat de fixture aan de selectie-criteria uit README.md voldoet."""
    rows = _load_csv(FINDINGS_CSV)
    assert len(rows) <= 20, f"fixture moet ≤20 rijen hebben, kreeg {len(rows)}"

    from collections import Counter

    cls_counts = Counter(r["classificatie"] for r in rows)
    herkomst_counts = Counter(r["herkomst"] for r in rows)

    # README §"Selectie-criteria" — afgezwakt voor NC: dataset bevat in
    # huidige bron alleen 27001-NC's; "≥1 9001-NC" criterium is niet
    # haalbaar zonder synthetische rijen.
    assert cls_counts["NC"] >= 2, f"<2 NC: {cls_counts}"
    assert cls_counts["OFI"] >= 6, f"<6 OFI: {cls_counts}"
    assert cls_counts["positief"] >= 4, f"<4 positief: {cls_counts}"
    assert herkomst_counts["Miro"] >= 2, f"<2 miro: {herkomst_counts}"


@pytest.mark.snapshot
@pytest.mark.skipif(
    importlib.util.find_spec("iso_audit.classification.findings") is None,
    reason="classifier nog niet gemigreerd (milestone B §2.2.5)",
)
def test_classifier_matches_snapshot() -> None:
    """Draai de gemigreerde classifier op `findings.csv`; byte-identiek match op antwoord-velden.

    Activeert automatisch zodra `iso_audit.classification.findings`
    geïmplementeerd is in milestone B §2.2.5.
    """
    pytest.skip("Classifier API-shape nog niet bevroren; vul deze test in tijdens §2.2.5 PR.")
