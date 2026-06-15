"""Tests voor `classifier` + `pattern_detection`."""

from __future__ import annotations

from iso_audit.memo.classifier import DefaultClassifier
from iso_audit.memo.models import Finding
from iso_audit.memo.pattern_detection import DefaultPatternDetector


def _f(fid: str, severity: str, clause: str = "10.2", promote: bool = False) -> Finding:
    return Finding(
        id=fid,
        severity=severity,  # type: ignore[arg-type]
        standard="iso-27001-2022",
        clause=clause,
        title=f"f{fid}",
        description="x",
        promote_to_improvement=promote,
    )


# --- classifier -------------------------------------------------------------


def test_ncs_alleen_nc_in_volgorde() -> None:
    fs = [_f("1", "OFI"), _f("2", "NC"), _f("3", "POSITIVE"), _f("4", "NC")]
    out = DefaultClassifier().ncs(fs)
    assert [f.id for f in out] == ["2", "4"]


def test_improvements_expliciete_promotie() -> None:
    fs = [_f("1", "OFI", "8.15", promote=True), _f("2", "OFI", "8.15")]
    out = DefaultClassifier().improvements(fs, threshold=99)
    assert [f.id for f in out] == ["1"]


def test_improvements_drempel_een_representant() -> None:
    fs = [_f(str(i), "OFI", "10.2") for i in range(3)] + [_f("x", "OFI", "5.11")]
    out = DefaultClassifier().improvements(fs, threshold=3)
    # 10.2 heeft 3 OFI's (>= drempel) → één representant; 5.11 heeft er 1 → niet.
    assert [f.id for f in out] == ["0"]


def test_improvements_geen_dubbeling_expliciet_en_drempel() -> None:
    fs = [_f("a", "OFI", "10.2", promote=True)] + [_f(str(i), "OFI", "10.2") for i in range(3)]
    out = DefaultClassifier().improvements(fs, threshold=2)
    # clausule 10.2 al gedekt door expliciete promotie → geen extra representant.
    assert [f.id for f in out] == ["a"]


def test_improvements_threshold_nul_alleen_expliciet() -> None:
    fs = [_f(str(i), "OFI", "10.2") for i in range(5)]
    out = DefaultClassifier().improvements(fs, threshold=0)
    assert out == []


# --- pattern detection ------------------------------------------------------


def test_pattern_gemengde_clausule() -> None:
    fs = [_f("1", "POSITIVE", "10.2"), _f("2", "OFI", "10.2"), _f("3", "OFI", "10.2")]
    note = DefaultPatternDetector().pattern_note("10.2", fs)
    assert note is not None
    assert "1 positieve bevinding" in note
    assert "2 OFI's" in note


def test_pattern_alleen_positief_geen_note() -> None:
    fs = [_f("1", "POSITIVE", "10.2")]
    assert DefaultPatternDetector().pattern_note("10.2", fs) is None


def test_pattern_alleen_ofi_geen_note() -> None:
    fs = [_f("1", "OFI", "10.2")]
    assert DefaultPatternDetector().pattern_note("10.2", fs) is None
