"""Tests voor `iso_audit.reporting.slide_summary` — gws gemockt."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

from iso_audit.reporting import slide_summary


def _bev(klasse: str, clausule: str = "10.2") -> dict[str, Any]:
    return {
        "classificatie": klasse,
        "clausule": clausule,
        "beschrijving": "iets",
        "document_naam": "Doc",
    }


def test_top3_prioriteert_nc_voor_ofi() -> None:
    bev = [_bev("OFI"), _bev("NC"), _bev("OFI"), _bev("NC")]
    top3 = slide_summary._top3_bevindingen(bev)
    # NC's eerst (2 NCs), dan een OFI.
    assert [b["classificatie"] for b in top3] == ["NC", "NC", "OFI"]


def test_top3_maximum_drie() -> None:
    bev = [_bev("OFI") for _ in range(10)]
    assert len(slide_summary._top3_bevindingen(bev)) == 3


def test_top3_leeg_bij_lege_input() -> None:
    assert slide_summary._top3_bevindingen([]) == []


def test_slide_requests_5_slides() -> None:
    """5 slides → 1 delete + 5 createSlide-requests."""
    bev = [_bev("NC"), _bev("OFI"), _bev("positief")]
    reqs = slide_summary._slide_requests(bev, "9001")
    create_slides = [r for r in reqs if "createSlide" in r]
    assert len(create_slides) == 5
    # Delete-default-slide aan het begin.
    assert reqs[0] == {"deleteObject": {"objectId": "p"}}


def test_slide_requests_norm_label_in_titel() -> None:
    bev = [_bev("NC")]
    reqs = slide_summary._slide_requests(bev, "beide")
    # Zoek de eerste insertText-request (slide 1 titel).
    insert_texts = [r for r in reqs if "insertText" in r]
    assert insert_texts
    tekst = insert_texts[0]["insertText"]["text"]
    assert "ISO 9001:2015 + ISO 27001:2022" in tekst


def test_slide_requests_telt_classificaties() -> None:
    bev = [_bev("NC"), _bev("NC"), _bev("OFI"), _bev("positief")]
    reqs = slide_summary._slide_requests(bev, "9001")
    # Slide 3 = Resultaatoverzicht; vind die insertText-body.
    all_texts = " ".join(r["insertText"]["text"] for r in reqs if "insertText" in r)
    assert "Non-conformiteiten (NC): 2" in all_texts
    assert "Kansen voor verbetering (OFI): 1" in all_texts
    assert "Positieve bevindingen: 1" in all_texts


def test_genereer_slides_volledige_flow() -> None:
    """create → batchUpdate → drive update (als folder_id is meegegeven)."""
    bev = [_bev("NC")]
    responses = [
        {"presentationId": "p-1"},  # create
        {},  # batchUpdate
        {},  # drive files update
    ]
    with patch.object(slide_summary, "_gws", side_effect=responses) as mock:
        out = slide_summary.genereer_slides(bev, "9001", folder_id="folder-abc")
    assert out == "p-1"
    assert mock.call_count == 3
    # Eerste call = slides create.
    assert mock.call_args_list[0].args[:3] == ("slides", "presentations", "create")


def test_genereer_slides_zonder_folder_skipt_move(
    monkeypatch: Any,
) -> None:
    monkeypatch.delenv("AUDIT_DRIVE_FOLDER_ID", raising=False)
    bev = [_bev("OFI")]
    responses = [{"presentationId": "p-1"}, {}]
    with patch.object(slide_summary, "_gws", side_effect=responses) as mock:
        slide_summary.genereer_slides(bev, "27001")
    # Slechts 2 calls: create + batchUpdate.
    assert mock.call_count == 2
