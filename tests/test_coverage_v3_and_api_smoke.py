from sentinel_ai_v2.v3 import SentinelV3
from sentinel_ai_v2.api import SentinelClient
from sentinel_ai_v2.config import SentinelConfig


def test_v3_evaluate_happy_path_minimal():
    s = SentinelV3()
    req = {
        "contract_version": 3,
        "component": "sentinel",
        "request_id": "r1",
        "telemetry": {"block_height": 10, "mempool_size": 1},
        "fail_closed": True,
    }
    out = s.evaluate(req)
    assert out["contract_version"] == 3
    assert out["component"] == "sentinel"
    assert out["request_id"] == "r1"
    assert out["decision"] in ("ALLOW", "BLOCK", "ERROR")
    assert "context_hash" in out
    assert "reason_codes" in out


def test_v3_evaluate_invalid_request_is_error():
    s = SentinelV3()
    out = s.evaluate("not a dict")  # type: ignore[arg-type]
    assert out["decision"] == "ERROR"


def test_api_client_smoke():
    client = SentinelClient(config=SentinelConfig())
    # SentinelClient should be able to run without a model file.
    result = client.evaluate({"block_height": 1, "mempool_size": 0})
    assert hasattr(result, "status")
    assert hasattr(result, "risk_score")
    assert hasattr(result, "details")
