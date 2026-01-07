from types import SimpleNamespace

import sentinel_ai_v2.adaptive_core_bridge as acb
from sentinel_ai_v2.adaptive_hooks import report_reorg_anomaly_to_adaptive
from sentinel_ai_v2.feedback_hooks import send_feedback_to_adaptive
from sentinel_ai_v2.heartbeat import shield_heartbeat


def test_bridge_unavailable_is_safe_noop():
    bridge = acb.SentinelAdaptiveCoreBridge()
    assert bridge.is_available is False
    # No exceptions:
    bridge.submit_simple_threat("x", "y", 1, "d")
    bridge.submit_feedback_label(layer="sentinel", feedback="true_positive", event_id="e1")
    assert "not available" in bridge.get_immune_report_text().lower()


def test_bridge_available_paths(monkeypatch):
    sent = {"packets": [], "feedback": [], "report": []}

    class DummyInterface:
        def submit_threat_packet(self, packet):
            sent["packets"].append(packet)

        def submit_feedback_events(self, events):
            sent["feedback"].append([(e.event_id, e.layer, e.feedback) for e in events])

        def get_immune_report_text(self, min_severity=0):
            return f"REPORT:{min_severity}"

        def get_adaptive_state(self):
            return SimpleNamespace(global_threshold=0.5, layer_weights={"sentinel": 1.0})

        def get_last_update_metadata(self):
            return {"last_threat_received": "t1", "last_learning_update": "t2"}

    class DummyPacket:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    # Force “available”
    monkeypatch.setattr(acb, "AdaptiveCoreInterface", DummyInterface)
    monkeypatch.setattr(acb, "ThreatPacket", DummyPacket)

    bridge = acb.SentinelAdaptiveCoreBridge(interface=DummyInterface())
    assert bridge.is_available is True

    bridge.submit_simple_threat(
        source_layer="sentinel",
        threat_type="reorg",
        severity=7,
        description="x",
        block_height=123,
        metadata={"k": "v"},
    )
    assert len(sent["packets"]) == 1
    assert sent["packets"][0].kwargs["severity"] == 7
    assert sent["packets"][0].kwargs["block_height"] == 123

    bridge.submit_feedback_label(layer="sentinel", feedback="true_positive", event_id="e1")
    assert sent["feedback"][0][0] == ("e1", "sentinel", "TRUE_POSITIVE")

    # Hooks
    report_reorg_anomaly_to_adaptive(456, 0.91, details={"x": 1}, bridge=bridge)
    assert len(sent["packets"]) == 2  # another packet emitted

    send_feedback_to_adaptive(layer="sentinel", event_id="e2", feedback="missed_attack", bridge=bridge)
    assert sent["feedback"][-1][0] == ("e2", "sentinel", "MISSED_ATTACK")

    # Heartbeat
    hb = shield_heartbeat(min_severity=3, bridge=bridge)
    assert "REPORT:3" in hb
    assert "Global Threshold" in hb
