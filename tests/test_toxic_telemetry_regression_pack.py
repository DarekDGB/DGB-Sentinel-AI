import pytest

import sentinel_ai_v2.contracts.v3_types as t
from sentinel_ai_v2.contracts.v3_reason_codes import ReasonCode
from sentinel_ai_v2.contracts.v3_types import SentinelV3Request


def _base_req(telemetry):
    return {
        "contract_version": 3,
        "component": "sentinel",
        "request_id": "tox",
        "telemetry": telemetry,
        "constraints": {"max_latency_ms": 2500},
    }


def test_rejects_bool_as_number():
    # bool is subclass of int; we explicitly reject it as a "number"
    req = _base_req({"x": True})
    with pytest.raises(ValueError) as e:
        SentinelV3Request.from_dict(req)
    assert e.value.args[0] == ReasonCode.SNTL_ERROR_BAD_NUMBER.value


def test_rejects_nan_and_inf():
    for bad in [float("nan"), float("inf"), float("-inf")]:
        req = _base_req({"x": bad})
        with pytest.raises(ValueError) as e:
            SentinelV3Request.from_dict(req)
        assert e.value.args[0] == ReasonCode.SNTL_ERROR_BAD_NUMBER.value


def test_rejects_non_string_dict_keys():
    req = _base_req({1: "x"})
    with pytest.raises(ValueError) as e:
        SentinelV3Request.from_dict(req)
    assert e.value.args[0] == ReasonCode.SNTL_ERROR_INVALID_REQUEST.value


def test_accepts_unicode_keys_and_values():
    tel = {"ключ": "значение", "emoji": "🔥", "nested": {"żółć": "gęślą"}}
    req = _base_req(tel)
    parsed = SentinelV3Request.from_dict(req)
    assert parsed.telemetry["emoji"] == "🔥"
    assert parsed.telemetry["nested"]["żółć"] == "gęślą"


def test_wide_dict_under_limits_is_accepted():
    tel = {f"k{i}": i for i in range(2000)}
    req = _base_req(tel)
    parsed = SentinelV3Request.from_dict(req)
    assert len(parsed.telemetry) == 2000


def test_large_list_under_limits_is_accepted():
    tel = {"arr": list(range(10_000))}
    req = _base_req(tel)
    parsed = SentinelV3Request.from_dict(req)
    assert len(parsed.telemetry["arr"]) == 10_000


def test_deep_nesting_hits_node_limit_when_forced_low(monkeypatch):
    # Make the node limit tiny to deterministically trigger the guard.
    monkeypatch.setattr(t.SentinelV3Request, "MAX_TELEMETRY_NODES", 50)

    deep = cur = {}
    for i in range(200):
        nxt = {"x": i}
        cur["n"] = nxt
        cur = nxt

    req = _base_req(deep)
    with pytest.raises(ValueError) as e:
        SentinelV3Request.from_dict(req)

    assert e.value.args[0] == ReasonCode.SNTL_ERROR_TELEMETRY_TOO_LARGE.value


def test_byte_limit_triggers_deterministically():
    # Exceed MAX_TELEMETRY_BYTES (200_000) with a single string value.
    req = _base_req({"blob": "a" * 300_000})
    with pytest.raises(ValueError) as e:
        SentinelV3Request.from_dict(req)
    assert e.value.args[0] == ReasonCode.SNTL_ERROR_TELEMETRY_TOO_LARGE.value


def test_fail_closed_is_deterministic_same_input_same_reason():
    req = _base_req({"blob": "a" * 300_000})

    for _ in range(3):
        with pytest.raises(ValueError) as e:
            SentinelV3Request.from_dict(req)
        assert e.value.args[0] == ReasonCode.SNTL_ERROR_TELEMETRY_TOO_LARGE.value
