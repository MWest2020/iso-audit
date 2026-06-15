"""Shape-tests voor het Sink Protocol.

Sink heeft in milestone A geen runtime-implementaties (eerste in milestone C),
dus de tests valideren alleen dat het Protocol en de payload-hierarchy correct
gedefinieerd zijn — geen runtime-gedrag.
"""

from __future__ import annotations

import dataclasses

import pytest

from iso_audit import sinks
from iso_audit.sinks.base import (
    MirrorPayload,
    NotificationPayload,
    ReportPayload,
    Sink,
    SinkPayload,
    SinkResult,
)


def test_sink_protocol_is_runtime_checkable() -> None:
    """Sink moet runtime_checkable zijn voor diagnostiek-doeleinden."""

    class _StubSink:
        naam = "stub"

        def send(self, payload: SinkPayload) -> SinkResult:
            return SinkResult(succes=True, bron_id=None, bericht="stub")

        def healthcheck(self) -> dict[str, object]:
            return {"status": "ok", "naam": self.naam}

    assert isinstance(_StubSink(), Sink)


@pytest.mark.parametrize(
    "payload_class",
    [ReportPayload, NotificationPayload, MirrorPayload],
)
def test_payload_classes_are_frozen_dataclasses(
    payload_class: type[SinkPayload],
) -> None:
    """Payloads horen frozen dataclasses te zijn — voorkomt mutatie tijdens
    door-de-pipeline-passing."""
    assert dataclasses.is_dataclass(payload_class)
    assert payload_class.__dataclass_params__.frozen  # type: ignore[attr-defined]


def test_payload_hierarchy_is_subtype_of_sinkpayload() -> None:
    """ReportPayload, NotificationPayload, MirrorPayload moeten alle drie
    SinkPayload erven — dat is het contract dat Sink-implementaties consumeren."""
    assert issubclass(ReportPayload, SinkPayload)
    assert issubclass(NotificationPayload, SinkPayload)
    assert issubclass(MirrorPayload, SinkPayload)


def test_sink_result_is_dataclass() -> None:
    """SinkResult is een dataclass voor structured returns; geen tuple-magic."""
    assert dataclasses.is_dataclass(SinkResult)


def test_register_adds_to_registry(lege_registries: None) -> None:
    """De Sink registry moet werken zoals Source en Notifier."""

    @sinks.register
    class _DriveSinkStub:
        naam = "drive-stub"

        def send(self, payload: SinkPayload) -> SinkResult:
            return SinkResult(succes=True, bron_id="abc", bericht="ok")

        def healthcheck(self) -> dict[str, object]:
            return {"status": "ok", "naam": self.naam}

    assert "drive-stub" in sinks.available()
    assert sinks.get("drive-stub") is _DriveSinkStub


def test_registry_bevat_minstens_drive() -> None:
    """In milestone C is DriveSink geregistreerd via `@register`."""
    import iso_audit.sinks.drive  # noqa: F401

    assert "drive" in sinks.available()
