"""Tests voor `iso_audit.sources.protocol_ingest.ingest_documenten`."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from iso_audit.sources.base import Document
from iso_audit.sources.protocol_ingest import ingest_documenten


class _FakeSource:
    """Minimale Source-adapter: twee documenten, eentje onleesbaar."""

    naam = "fake"

    def list_documents(self, filter: dict[str, object] | None = None) -> Iterator[Document]:
        del filter
        yield Document(
            id="ISO-1",
            titel="Issue 1",
            bron="fake",
            type="issue",
            laatst_gewijzigd="2026-05-01T10:00:00Z",
            inhoud_uri="fake://ISO-1",
        )
        yield Document(
            id="ISO-2",
            titel="Issue 2",
            bron="fake",
            type="issue",
            laatst_gewijzigd="2026-05-02T10:00:00Z",
            inhoud_uri="fake://ISO-2",
        )

    def fetch_content(self, doc: Document) -> str:
        if doc.id == "ISO-2":
            raise OSError("kan ISO-2 niet lezen")
        return f"inhoud van {doc.id}"


def test_ingest_documenten_mapt_naar_pipeline_dict(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("iso_audit.sources.get", lambda naam: _FakeSource)
    docs = ingest_documenten("fake")
    # ISO-2 is onleesbaar → overgeslagen (niet fataal); alleen ISO-1 blijft over.
    assert len(docs) == 1
    d = docs[0]
    assert d["naam"] == "Issue 1"
    assert d["id"] == "ISO-1"
    assert d["tekst"] == "inhoud van ISO-1"
    assert d["mime_type"] == "issue"
    assert d["modified_at"] == "2026-05-01T10:00:00Z"
    # herkomst = bronnaam met hoofdletter, zodat de bevinding terug te voeren is.
    assert d["herkomst"] == "Fake"


def test_ingest_documenten_onbekende_bron_raiset() -> None:
    with pytest.raises(KeyError):
        ingest_documenten("bestaat-niet")
