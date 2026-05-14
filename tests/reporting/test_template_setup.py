"""Tests voor `iso_audit.reporting.template_setup` — gws gemockt."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

from iso_audit.reporting import template_setup

# ---------- _load_structure ----------


def test_load_structure_geeft_dict() -> None:
    s = template_setup._load_structure()
    assert "versie" in s
    assert "normen" in s
    assert "secties" in s


# ---------- _build_template_requests ----------


def test_build_template_requests_één_request() -> None:
    structure: dict[str, Any] = {
        "versie": "1.0",
        "normen": ["ISO 9001"],
        "secties": [
            {"titel": "1. Samenvatting", "placeholders": [{"naam": "summary"}]},
        ],
    }
    reqs = template_setup._build_template_requests(structure)
    assert len(reqs) == 1
    assert "insertText" in reqs[0]
    tekst = reqs[0]["insertText"]["text"]
    assert "1. Samenvatting" in tekst
    assert "{{  summary  }}" in tekst


def test_build_template_requests_bevat_versie() -> None:
    structure = {"versie": "2.5", "normen": ["X"], "secties": []}
    reqs = template_setup._build_template_requests(structure)
    assert "2.5" in reqs[0]["insertText"]["text"]


# ---------- _find_existing_report ----------


def test_find_existing_report_match() -> None:
    response = {"files": [{"id": "doc-1", "name": "Auditrapport 2026"}]}
    with patch.object(template_setup, "_gws", return_value=response):
        out = template_setup._find_existing_report("folder-x")
    assert out == "doc-1"


def test_find_existing_report_geen_match() -> None:
    with patch.object(template_setup, "_gws", return_value={"files": []}):
        assert template_setup._find_existing_report("folder-x") is None


# ---------- create_template ----------


def test_create_template_happy_path() -> None:
    # gws-calls: 1) drive files create  2) docs batchUpdate  3) drive files update
    responses = [
        {"id": "new-doc-id"},  # create
        {},  # batchUpdate
        {},  # update (folder move)
    ]
    with patch.object(template_setup, "_gws", side_effect=responses) as mock:
        out = template_setup.create_template(folder_id="folder-abc")
    assert out == "new-doc-id"
    assert mock.call_count == 3
    # Eerste call = drive create.
    first = mock.call_args_list[0]
    assert first.args[:3] == ("drive", "files", "create")
    # Tweede call = docs batchUpdate met de juiste documentId.
    second = mock.call_args_list[1]
    assert second.args[:3] == ("docs", "documents", "batchUpdate")
    assert second.kwargs["params"]["documentId"] == "new-doc-id"
    # Derde call = drive files update met folder-add.
    third = mock.call_args_list[2]
    assert third.kwargs["params"]["addParents"] == "folder-abc"


def test_create_template_zonder_folder_skipt_move() -> None:
    """`folder_id=""` → geen Drive-move-call."""
    responses = [{"id": "doc-1"}, {}]
    with patch.object(template_setup, "_gws", side_effect=responses) as mock:
        template_setup.create_template(folder_id="")
    assert mock.call_count == 2  # alleen create + batchUpdate


# ---------- verify_placeholders ----------


def test_verify_placeholders_alles_aanwezig() -> None:
    # Structure heeft "summary" + "details".
    structure = {
        "versie": "1.0",
        "normen": ["X"],
        "secties": [
            {"titel": "S", "placeholders": [{"naam": "summary"}, {"naam": "details"}]},
        ],
    }
    doc_body = {
        "body": {
            "content": [
                {
                    "paragraph": {
                        "elements": [{"textRun": {"content": "{{summary}} en {{details}}"}}]
                    }
                }
            ]
        }
    }
    with (
        patch.object(template_setup, "_load_structure", return_value=structure),
        patch.object(template_setup, "_gws", return_value=doc_body),
    ):
        missing = template_setup.verify_placeholders("d1")
    assert missing == []


def test_verify_placeholders_ontbrekend() -> None:
    structure = {
        "versie": "1.0",
        "normen": ["X"],
        "secties": [
            {"titel": "S", "placeholders": [{"naam": "alpha"}, {"naam": "beta"}]},
        ],
    }
    doc_body = {
        "body": {"content": [{"paragraph": {"elements": [{"textRun": {"content": "{{alpha}}"}}]}}]}
    }
    with (
        patch.object(template_setup, "_load_structure", return_value=structure),
        patch.object(template_setup, "_gws", return_value=doc_body),
    ):
        missing = template_setup.verify_placeholders("d1")
    assert missing == ["beta"]
