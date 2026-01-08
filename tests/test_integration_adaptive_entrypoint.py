import math

from sentinel_ai_v2.api import evaluate_v3
from tests.fixtures_v3 import make_valid_v3_request


def test_adaptive_core_entrypoint_valid_request_is_not_error():
    """
    Golden integration test:
    Adaptive Core calls ONLY sentinel_ai_v2.api.evaluate_v3(request) -> dict.

    For a valid v3 request, decision must not be ERROR and contract-stable
    fields must exist.
    """
    req = make_valid_v3_request(
        request_id="adaptive-golden",
        telemetry={"block_height": 10, "mempool_size": 1, "entropy": {"score": 0.1}},
        max_latency_ms=2500,
    )

    out = evaluate_v3(req)

    assert out["contract_version"] == 3
    assert out["component"] == "sentinel"
    assert out["request_id"] == "adaptive-golden"
    assert isinstance(out["context_hash"], str) and len(out["context_hash"]) == 64

    assert out["decision"] in {"ALLOW", "WARN", "BLOCK"}
    assert "reason_codes" in out
    assert "meta" in out and out["meta"].get("fail_closed") is True


def test_adaptive_core_entrypoint_fail_closed_unknown_top_level_key():
    req = make_valid_v3_request(request_id="bad-unknown-top")
    req["unknown_key"] = True  # must be rejected

    out = evaluate_v3(req)

    assert out["contract_version"] == 3
    assert out["component"] == "sentinel"
    assert out["request_id"] == "bad-unknown-top"
    assert out["decision"] == "ERROR"
    assert out["meta"].get("fail_closed") is True


def test_adaptive_core_entrypoint_fail_closed_nan_in_telemetry():
    req = make_valid_v3_request(
        request_id="bad-nan",
        telemetry={"block_height": 10, "entropy": {"score": math.nan}},
    )

    out = evaluate_v3(req)

    assert out["contract_version"] == 3
    assert out["component"] == "sentinel"
    assert out["request_id"] == "bad-nan"
    assert out["decision"] == "ERROR"
    assert out["meta"].get("fail_closed") is True


def test_adaptive_core_entrypoint_fail_closed_bad_contract_version():
    req = make_valid_v3_request(request_id="bad-version", contract_version=2)

    out = evaluate_v3(req)

    assert out["contract_version"] == 3
    assert out["component"] == "sentinel"
    assert out["request_id"] == "bad-version"
    assert out["decision"] == "ERROR"
    assert out["meta"].get("fail_closed") is True
