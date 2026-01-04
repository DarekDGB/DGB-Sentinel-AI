from sentinel_ai_v2.api import SentinelClient
from sentinel_ai_v2.config import CircuitBreakerThresholds, SentinelConfig
from sentinel_ai_v2.v3 import SentinelV3


def test_v2_v3_no_behavior_drift_minimal_snapshot():
    """
    Regression lock:
    For the same telemetry input, v2 result must match the v3-bridged payload.
    This prevents silent behavior changes during the v3 migration.
    """

    # Minimal valid telemetry snapshot (intentionally sparse)
    raw_telemetry = {}

    # Construct config with defaults
    cfg = SentinelConfig(
        circuit_breakers=CircuitBreakerThresholds(),
        model_path=None,
        model_hash=None,
    )

    client = SentinelClient(cfg)
    v2_result = client.evaluate_snapshot(raw_telemetry)

    v3 = SentinelV3(thresholds=cfg.circuit_breakers, model=None)
    v3_resp = v3.evaluate(
        {
            "contract_version": 3,
            "component": "sentinel",
            "request_id": "test",
            "telemetry": raw_telemetry,
            "constraints": {"fail_closed": True},
        }
    )

    v3_details = (v3_resp.get("evidence") or {}).get("details") or {}
    assert v2_result.status == v3_details.get("v2_status")
    assert v2_result.risk_score == float(v3_details.get("v2_risk_score"))
    assert v2_result.details == v3_details.get("v2_details")
