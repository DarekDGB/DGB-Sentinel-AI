import pytest

from sentinel_ai_v2.contracts.v3_types import SentinelV3Request
from sentinel_ai_v2.contracts.v3_reason_codes import ReasonCode


def _base_req():
    return {
        "contract_version": 3,
        "component": "sentinel",
        "request_id": "r1",
        "telemetry": {"block_height": 1, "mempool_size": 2},
        "fail_closed": True,
    }


def test_component_must_match():
    req = _base_req()
    req["component"] = "nope"
    with pytest.raises(ValueError) as e:
        SentinelV3Request.from_dict(req)
    assert ReasonCode.SNTL_ERROR_INVALID_REQUEST.value in str(e.value)


def test_telemetry_too_large_fails_closed():
    req = _base_req()
    # Build a large telemetry payload
    req["telemetry"] = {"x": "a" * 200_000}
    with pytest.raises(ValueError) as e:
        SentinelV3Request.from_dict(req)
    assert ReasonCode.SNTL_ERROR_TELEMETRY_TOO_LARGE.value in str(e.value)


def test_unknown_top_level_key_fails_closed():
    req = _base_req()
    req["evil"] = 1
    with pytest.raises(ValueError) as e:
        SentinelV3Request.from_dict(req)
    assert ReasonCode.SNTL_ERROR_UNKNOWN_TOP_LEVEL_KEY.value in str(e.value)
