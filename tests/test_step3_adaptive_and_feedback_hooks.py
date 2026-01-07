import logging
import pytest

import sentinel_ai_v2.adaptive_bridge as ab
import sentinel_ai_v2.adaptive_hooks as ah
import sentinel_ai_v2.feedback_hooks as fh


# -----------------------------
# adaptive_bridge.py
# -----------------------------

def test_build_adaptive_event_normalizes_fields():
    evt = ab.build_adaptive_event(
        anomaly_type="entropy_drop",
        severity=0.7,
        qri_before=0.2,
        qri_after=0.1,
        layer="sentinel",
        block_height=123,
        txid="tx1",
        was_mitigated=True,
        details="hello",
    )
    assert evt.layer == "sentinel"
    assert evt.anomaly_type == "entropy_drop"
    assert evt.severity == 0.7
    assert evt.qri_before == 0.2
    assert evt.qri_after == 0.1
    assert evt.block_height == 123
    assert evt.txid == "tx1"
    assert evt.was_mitigated is True
    assert evt.details == "hello"


def test_emit_adaptive_event_logs_json(caplog):
    evt = ab.build_adaptive_event(
        anomaly_type="mempool_anomaly",
        severity=0.4,
        qri_before=0.4,
        qri_after=0.3,
        details="x",
    )

    caplog.set_level(logging.DEBUG)
    ab.emit_adaptive_event(evt)

    joined = "\n".join(r.message for r in caplog.records)
    assert "AdaptiveEvent" in joined
    # ensure we're actually dumping a structured payload
    assert "anomaly_type" in joined


def test_export_to_adaptive_core_calls_emit(monkeypatch):
    called = {"n": 0}

    def _fake_emit(_evt):
        called["n"] += 1

    monkeypatch.setattr(ab, "emit_adaptive_event", _fake_emit)

    evt = ab.build_adaptive_event(anomaly_type="x", severity=0.1)
    ab.export_to_adaptive_core(evt)
    assert called["n"] == 1


def test_emit_adaptive_event_from_signal_clamps_qri_after_and_serializes_context(monkeypatch):
    captured = {}

    def _fake_export(evt):
        captured["evt"] = evt

    monkeypatch.setattr(ab, "export_to_adaptive_core", _fake_export)

    ab.emit_adaptive_event_from_signal(
        signal_name="sig",
        severity=0.5,
        qri_delta=-9.0,  # forces clamp to 0.0
        context={"b": 2, "a": 1},
        block_height=7,
        txid="t",
    )

    evt = captured["evt"]
    assert evt.anomaly_type == "sig"
    assert evt.qri_before == 0.5
    assert evt.qri_after == 0.0  # clamped
    assert evt.block_height == 7
    assert evt.txid == "t"
    # deterministic JSON ordering
    assert evt.details == '{"a":1,"b":2}'


def test_emit_adaptive_event_from_signal_context_fallback_to_str(monkeypatch):
    captured = {}

    def _fake_export(evt):
        captured["evt"] = evt

    monkeypatch.setattr(ab, "export_to_adaptive_core", _fake_export)

    # Create an unserializable object to force json.dumps exception path
    class Bad:
        def __repr__(self):
            return "BADCTX"

    ctx = {"x": Bad()}

    # Force json.dumps to raise so we test the fallback explicitly
    monkeypatch.setattr(ab.json, "dumps", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))

    ab.emit_adaptive_event_from_signal(
        signal_name="sig2",
        severity=0.2,
        qri_delta=0.0,
        context=ctx,
    )

    evt = captured["evt"]
    assert evt.anomaly_type == "sig2"
    # fallback should be str(context)
    assert "BADCTX" in (evt.details or "")


# -----------------------------
# adaptive_hooks.py
# -----------------------------

class _BridgeUnavailable:
    is_available = False

    def submit_simple_threat(self, *a, **k):
        raise AssertionError("should not be called when unavailable")


class _BridgeAvailable:
    is_available = True

    def __init__(self):
        self.calls = []

    def submit_simple_threat(self, **kwargs):
        self.calls.append(kwargs)


def test_report_reorg_anomaly_noop_when_bridge_unavailable():
    bridge = _BridgeUnavailable()
    ah.report_reorg_anomaly_to_adaptive(
        block_height=100,
        score=0.9,
        details={"x": 1},
        bridge=bridge,  # should no-op
    )


def test_report_reorg_anomaly_maps_severity_and_merges_metadata():
    bridge = _BridgeAvailable()
    ah.report_reorg_anomaly_to_adaptive(
        block_height=200,
        score=0.66,  # round(6.6) -> 7
        details={"window": "30s"},
        bridge=bridge,
    )

    assert len(bridge.calls) == 1
    call = bridge.calls[0]
    assert call["source_layer"] == "sentinel_ai_v2"
    assert call["threat_type"] == "reorg_pattern"
    assert call["severity"] == 7
    assert call["block_height"] == 200
    assert call["metadata"]["score"] == 0.66
    assert call["metadata"]["window"] == "30s"


# -----------------------------
# feedback_hooks.py
# -----------------------------

class _FeedbackBridgeUnavailable:
    is_available = False

    def submit_feedback_label(self, *a, **k):
        raise AssertionError("should not be called when unavailable")


class _FeedbackBridgeAvailable:
    is_available = True

    def __init__(self):
        self.calls = []

    def submit_feedback_label(self, **kwargs):
        self.calls.append(kwargs)


def test_send_feedback_noop_when_bridge_unavailable():
    fh.send_feedback_to_adaptive(
        layer="sentinel_ai_v2",
        event_id="e1",
        feedback="true_positive",
        bridge=_FeedbackBridgeUnavailable(),
    )


def test_send_feedback_uppercases_and_calls_bridge():
    bridge = _FeedbackBridgeAvailable()
    fh.send_feedback_to_adaptive(
        layer="sentinel_ai_v2",
        event_id="e2",
        feedback="missed_attack",
        bridge=bridge,
    )

    assert len(bridge.calls) == 1
    call = bridge.calls[0]
    assert call["layer"] == "sentinel_ai_v2"
    assert call["event_id"] == "e2"
    assert call["feedback"] == "MISSED_ATTACK"
