from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .config import CircuitBreakerThresholds, SentinelConfig
from .model_loader import LoadedModel, load_and_verify_model
from .v3 import SentinelV3


@dataclass
class SentinelResult:
    """Public, simplified result returned by SentinelClient."""
    status: str
    risk_score: float
    details: list[str]


class SentinelClient:
    """
    High-level interface for consuming Sentinel AI v2 from ADN or other services.
    """

    def __init__(self, config: SentinelConfig) -> None:
        self._config = config
        self._thresholds: CircuitBreakerThresholds = config.circuit_breakers

        # Model is optional – if file or hash not provided, we simply skip loading.
        self._model: LoadedModel | None = None
        if config.model_path:
            try:
                self._model = load_and_verify_model(
                    model_path=config.model_path,
                    expected_hash=config.model_hash,
                )
            except Exception:
                # Fail-open approach: system continues using non-ML signals only.
                self._model = None

        # v3 evaluator (internal)
        self._v3 = SentinelV3(thresholds=self._thresholds, model=self._model)

    def evaluate_snapshot(self, raw_telemetry: Dict[str, Any]) -> SentinelResult:
        """
        Evaluate a single telemetry snapshot and return a compact public result.

        NOTE: v2 public API preserved.
        Internally routes through Shield Contract v3 evaluator (adapter).
        """
        request_v3 = {
            "contract_version": 3,
            "component": "sentinel",
            "request_id": "v2-evaluate_snapshot",
            "telemetry": raw_telemetry,
            "constraints": {"fail_closed": True},
        }

        response_v3 = self._v3.evaluate(request_v3)

        # Fail-closed: if v3 errors, return a safe v2-shaped failure
        if response_v3.get("decision") == "ERROR":
            return SentinelResult(
                status="ERROR",
                risk_score=0.0,
                details=["SENTINEL_V3_ERROR"],
            )

        # Map back to v2 output exactly using the compatibility payload
        details = (((response_v3.get("evidence") or {}).get("details")) or {})
        v2_status = details.get("v2_status", "ERROR")
        v2_risk_score = float(details.get("v2_risk_score", 0.0))
        v2_details = details.get("v2_details", ["SENTINEL_V3_MISSING_V2_PAYLOAD"])

        return SentinelResult(
            status=v2_status,
            risk_score=v2_risk_score,
            details=list(v2_details),
        )
