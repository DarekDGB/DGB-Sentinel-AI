from __future__ import annotations

import io
import runpy
import sys
import types

import pytest

import sentinel_ai_v2.adaptive_core_bridge as acb
import sentinel_ai_v2.cli as cli
import sentinel_ai_v2.contracts.v3_hash as v3_hash
import sentinel_ai_v2.v3 as v3mod
from sentinel_ai_v2.api import SentinelClient
from sentinel_ai_v2.circuit_breakers import evaluate_circuit_breakers
from sentinel_ai_v2.config import CircuitBreakerThresholds, SentinelConfig
from sentinel_ai_v2.contracts.v3_reason_codes import ReasonCode
from sentinel_ai_v2.contracts.v3_types import SentinelV3Request, _safe_is_finite_number, _walk_check_finite
from sentinel_ai_v2.heartbeat import shield_heartbeat
from sentinel_ai_v2.telemetry_monitor import check_block_progress, init_block_progress_monitor
from sentinel_ai_v2.v3 import SentinelV3
from sentinel_ai_v2.wrapper.sentinel_wrapper import SentinelWrapper
from sentinel_ai_v2.wrapper.workflow import _get_client, run_full_workflow


def _base_v3_request() -> dict:
    return {
        "contract_version": 3,
        "component": "sentinel",
        "request_id": "coverage-lock",
        "telemetry": {"entropy": {"score": 0.1}, "mempool": {"score": 0.1}, "reorg": {"score": 0.1}},
        "constraints": {"max_latency_ms": 2500},
    }


def test_adaptive_core_bridge_import_success_path(monkeypatch):
    fake_interface_module = types.ModuleType("adaptive_core.interface")
    fake_packet_module = types.ModuleType("adaptive_core.threat_packet")

    class FakeInterface:
        def __init__(self):
            self.threats = []

        def submit_threat_packet(self, packet):
            self.threats.append(packet)

        def submit_feedback_events(self, events):
            self.feedback_events = list(events)

        def get_immune_report_text(self, min_severity=0):
            return f"immune:{min_severity}"

        def get_adaptive_state(self):
            return types.SimpleNamespace(
                global_threshold=0.5,
                layer_weights={"entropy": 1.0},
                feedback_counts={"TRUE_POSITIVE": 1},
            )

        def get_last_update_metadata(self):
            return {"last_threat_received": "t1", "last_learning_update": "t2"}

    class FakeThreatPacket:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    fake_interface_module.AdaptiveCoreInterface = FakeInterface
    fake_packet_module.ThreatPacket = FakeThreatPacket

    monkeypatch.setitem(sys.modules, "adaptive_core", types.ModuleType("adaptive_core"))
    monkeypatch.setitem(sys.modules, "adaptive_core.interface", fake_interface_module)
    monkeypatch.setitem(sys.modules, "adaptive_core.threat_packet", fake_packet_module)

    reloaded = __import__("importlib").reload(acb)
    bridge = reloaded.SentinelAdaptiveCoreBridge()

    assert bridge.is_available is True
    bridge.submit_simple_threat("sentinel", "entropy", 5, "drop", metadata={"a": 1})
    assert bridge._interface.threats[0].kwargs["threat_type"] == "entropy"

    bridge.submit_feedback_label(layer="sentinel", feedback="true_positive", event_id="abc")
    assert bridge._interface.feedback_events[0].feedback == "TRUE_POSITIVE"
    assert bridge.get_immune_report_text(min_severity=3) == "immune:3"
    heartbeat = shield_heartbeat(min_severity=2, bridge=bridge)
    assert "DigiByte Quantum Shield" in heartbeat
    assert "immune:2" in heartbeat

    monkeypatch.delitem(sys.modules, "adaptive_core.interface", raising=False)
    monkeypatch.delitem(sys.modules, "adaptive_core.threat_packet", raising=False)
    __import__("importlib").reload(acb)


def test_v2_client_fail_closed_when_v3_errors(monkeypatch):
    client = SentinelClient(SentinelConfig())
    object.__setattr__(client, "_v3", types.SimpleNamespace(evaluate=lambda request: {"decision": "ERROR"}))

    result = client.evaluate_snapshot({"bad": object()})

    assert result.status == "ERROR"
    assert result.risk_score == 0.0
    assert result.details == ["SENTINEL_V3_ERROR"]


def test_circuit_breaker_combo_triggers():
    thresholds = CircuitBreakerThresholds(
        entropy_drop_threshold=0.5,
        mempool_anomaly_threshold=0.5,
        reorg_depth_threshold=2,
    )
    outcome = evaluate_circuit_breakers(
        {"entropy_drop": 0.5, "mempool_anomaly": 0.5, "reorg_depth": 2},
        thresholds,
    )

    assert outcome.triggered is True
    assert outcome.reasons == ["combo: entropy + mempool + reorg"]


def test_cli_unknown_command_branch(monkeypatch):
    class Parser:
        def parse_args(self, argv):
            return types.SimpleNamespace(command="unknown")

        def error(self, message):
            raise RuntimeError(message)

    monkeypatch.setattr(cli, "_build_parser", lambda: Parser())

    with pytest.raises(RuntimeError, match="Unknown command"):
        cli.main([])


def test_cli_unknown_command_return_branch(monkeypatch):
    class Parser:
        def parse_args(self, argv):
            return types.SimpleNamespace(command="unknown")

        def error(self, message):
            self.message = message

    monkeypatch.setattr(cli, "_build_parser", lambda: Parser())

    assert cli.main([]) == 1


def test_cli_main_module_entrypoint_version(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["sentinel-ai", "version"])
    monkeypatch.setattr(sys, "stdout", io.StringIO())
    monkeypatch.delitem(sys.modules, "sentinel_ai_v2.cli", raising=False)

    with pytest.raises(SystemExit) as exc:
        runpy.run_module("sentinel_ai_v2.cli", run_name="__main__")

    assert exc.value.code == 0


def test_v3_hash_misconfiguration_fails_closed(monkeypatch):
    monkeypatch.setattr(v3_hash, "HASH_ALGO_V3", "sha512")

    with pytest.raises(RuntimeError, match="misconfigured"):
        v3_hash.canonical_hash_v3({"x": 1})


def test_v3_types_remaining_contract_guards():
    assert _safe_is_finite_number(True) is False
    assert _safe_is_finite_number(float("inf")) is False

    with pytest.raises(ValueError) as non_dict:
        SentinelV3Request.from_dict([])  # type: ignore[arg-type]
    assert ReasonCode.SNTL_ERROR_INVALID_REQUEST.value in str(non_dict.value)

    req = _base_v3_request()
    req["request_id"] = 123
    req["constraints"] = {"max_latency_ms": object()}
    parsed = SentinelV3Request.from_dict(req)
    assert parsed.request_id == "123"
    assert parsed.constraints.max_latency_ms == 2500

    bad_component_req = _base_v3_request()
    bad_component_req["component"] = 7
    with pytest.raises(ValueError) as bad_component:
        SentinelV3Request.from_dict(bad_component_req)
    assert ReasonCode.SNTL_ERROR_INVALID_REQUEST.value in str(bad_component.value)

    bad_telemetry_req = _base_v3_request()
    bad_telemetry_req["telemetry"] = []
    with pytest.raises(ValueError) as bad_telemetry:
        SentinelV3Request.from_dict(bad_telemetry_req)
    assert ReasonCode.SNTL_ERROR_INVALID_REQUEST.value in str(bad_telemetry.value)

    bad_key_req = _base_v3_request()
    bad_key_req["telemetry"] = {1: "bad-key"}
    with pytest.raises(ValueError) as bad_key:
        SentinelV3Request.from_dict(bad_key_req)
    assert ReasonCode.SNTL_ERROR_INVALID_REQUEST.value in str(bad_key.value)

    class NotJson:
        pass

    unserializable_req = _base_v3_request()
    unserializable_req["telemetry"] = {"x": NotJson()}
    with pytest.raises(ValueError) as unserializable:
        SentinelV3Request.from_dict(unserializable_req)
    assert ReasonCode.SNTL_ERROR_INVALID_REQUEST.value in str(unserializable.value)

    assert _walk_check_finite([float("nan")], max_nodes=10) == ReasonCode.SNTL_ERROR_BAD_NUMBER
    assert _walk_check_finite(float("nan"), max_nodes=10) == ReasonCode.SNTL_ERROR_BAD_NUMBER

    bad_number_req = _base_v3_request()
    bad_number_req["telemetry"] = {"items": [1, float("nan")], "direct": float("inf")}
    with pytest.raises(ValueError) as bad_number:
        SentinelV3Request.from_dict(bad_number_req)
    assert ReasonCode.SNTL_ERROR_BAD_NUMBER.value in str(bad_number.value)



def test_heartbeat_unavailable_branch():
    class UnavailableBridge:
        is_available = False

    assert shield_heartbeat(bridge=UnavailableBridge()) == "Shield heartbeat: Adaptive Core not available."


class _Rpc:
    def __init__(self):
        self.height = 777

    def get_block_count(self):
        return self.height


def test_block_progress_module_level_helpers(monkeypatch):
    import sentinel_ai_v2.telemetry_monitor as tm

    monkeypatch.setattr(tm, "_monitor", None)
    with pytest.raises(RuntimeError, match="not initialised"):
        check_block_progress()

    init_block_progress_monitor(_Rpc(), stall_threshold_seconds=1)
    status = check_block_progress()
    assert status.current_height == 777


def test_v3_remaining_branches(monkeypatch):
    sentinel = SentinelV3(CircuitBreakerThresholds())

    def explode(_request):
        raise TypeError("boom")

    monkeypatch.setattr(v3mod.SentinelV3Request, "from_dict", explode)
    out = sentinel.evaluate(_base_v3_request())
    assert out["decision"] == "ERROR"
    assert out["reason_codes"] == [ReasonCode.SNTL_ERROR_INVALID_REQUEST.value]

    assert sentinel._tier_from_score(0.49) == "MEDIUM"
    assert sentinel._tier_from_score(0.74) == "HIGH"
    assert sentinel._tier_from_score(0.75) == "CRITICAL"

    assert sentinel._map_status_to_decision("ok") == "ALLOW"
    assert sentinel._map_status_to_decision("warn") == "WARN"
    assert sentinel._map_status_to_decision("error") == "ERROR"
    assert sentinel._map_status_to_decision("unexpected") == "BLOCK"

    class BrokenThresholds:
        def __getattribute__(self, name):
            if name == "__dict__":
                raise RuntimeError("no vars")
            return object.__getattribute__(self, name)

    assert sentinel._thresholds_fingerprint(BrokenThresholds()) == {"_": "unavailable"}


def test_wrapper_default_client_paths(monkeypatch):
    class DummyClient:
        def __init__(self, config=None):
            self.config = config
            self.seen = None

        def evaluate_snapshot(self, raw_telemetry):
            self.seen = raw_telemetry
            return types.SimpleNamespace(status="OK", risk_score=0.01, details=[])

    monkeypatch.setattr("sentinel_ai_v2.wrapper.workflow.SentinelClient", DummyClient)
    workflow_result = run_full_workflow({"height": 1})
    assert workflow_result.status == "OK"

    default_client = _get_client()
    assert isinstance(default_client, DummyClient)

    monkeypatch.setattr("sentinel_ai_v2.wrapper.sentinel_wrapper.SentinelClient", DummyClient)
    wrapper = SentinelWrapper()
    wrapped_result = wrapper.evaluate({"height": 2})
    assert wrapped_result.status == "OK"
    assert wrapper.last_status()["status"] == "OK"
