from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import time

from .config import CircuitBreakerThresholds
from .data_intake import TelemetrySnapshot, normalize_raw_telemetry
from .model_loader import LoadedModel, run_model_inference
from .scoring import SentinelScore, compute_risk_score

from .contracts import ReasonCode, SentinelV3Request, canonical_sha256


@dataclass(frozen=True)
class SentinelV3:
    thresholds: CircuitBreakerThresholds
    model: Optional[LoadedModel] = None

    COMPONENT: str = "sentinel"
    CONTRACT_VERSION: int = 3

    def evaluate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()

        # Strict contract parsing (fail-closed)
        try:
            req = SentinelV3Request.from_dict(request)
        except ValueError as e:
            reason = str(e) or ReasonCode.SNTL_ERROR_INVALID_REQUEST.value
            return self._error_response(
                request_id=request.get("request_id", "unknown") if isinstance(request, dict) else "unknown",
                reason_code=reason,
                details={"error": reason},
                latency_ms=self._latency_ms(start),
            )
        except Exception:
            return self._error_response(
                request_id=request.get("request_id", "unknown") if isinstance(request, dict) else "unknown",
                reason_code=ReasonCode.SNTL_ERROR_INVALID_REQUEST.value,
                details={"error": "invalid request"},
                latency_ms=self._latency_ms(start),
            )

        # Version hard check
        if req.contract_version != self.CONTRACT_VERSION:
            return self._error_response(
                request_id=req.request_id,
                reason_code=ReasonCode.SNTL_ERROR_SCHEMA_VERSION.value,
                details={"error": "contract_version must be 3"},
                latency_ms=self._latency_ms(start),
            )

        # Component hard check
        if req.component != self.COMPONENT:
            return self._error_response(
                request_id=req.request_id,
                reason_code=ReasonCode.SNTL_ERROR_INVALID_REQUEST.value,
                details={"error": "component mismatch"},
                latency_ms=self._latency_ms(start),
            )

        # Existing v2 pipeline (unchanged behavior)
        snapshot: TelemetrySnapshot = normalize_raw_telemetry(req.telemetry)

        features: Dict[str, Any] = {
            "entropy_score": (snapshot.entropy or {}).get("score", 0.0),
            "mempool_score": (snapshot.mempool or {}).get("score", 0.0),
            "reorg_score": (snapshot.reorg or {}).get("score", 0.0),
            "entropy_drop": (snapshot.entropy or {}).get("drop", 0.0),
            "mempool_anomaly": (snapshot.mempool or {}).get("anomaly", 0.0),
            "reorg_depth": (snapshot.reorg or {}).get("depth", 0),
        }

        model_used = False
        if self.model is not None:
            features["model_score"] = run_model_inference(self.model, features)
            model_used = True

        sentinel_score: SentinelScore = compute_risk_score(features=features, thresholds=self.thresholds)

        context_hash = canonical_sha256(
            {
                "component": self.COMPONENT,
                "contract_version": self.CONTRACT_VERSION,
                "telemetry": req.telemetry,
                "thresholds": self._thresholds_fingerprint(self.thresholds),
                "model_used": bool(model_used),
            }
        )

        decision = self._map_status_to_decision(sentinel_score.status)

        # Stable reason codes: keep minimal and contract-facing
        reason_codes = [ReasonCode.SNTL_OK.value] if not sentinel_score.details else [ReasonCode.SNTL_V2_SIGNAL.value]

        return {
            "contract_version": self.CONTRACT_VERSION,
            "component": self.COMPONENT,
            "request_id": req.request_id,
            "context_hash": context_hash,
            "decision": decision,
            "risk": {"score": float(sentinel_score.risk_score), "tier": self._tier_from_score(float(sentinel_score.risk_score))},
            "reason_codes": reason_codes,
            "evidence": {
                "features": {},  # keep empty to avoid leaking internals
                "details": {
                    "v2_status": sentinel_score.status,
                    "v2_risk_score": float(sentinel_score.risk_score),
                    "v2_details": list(sentinel_score.details),
                },
            },
            "meta": {
                "model_used": bool(model_used),
                "latency_ms": self._latency_ms(start),
                "fail_closed": True,
            },
        }

    @staticmethod
    def _latency_ms(start: float) -> int:
        return int((time.time() - start) * 1000)

    @staticmethod
    def _tier_from_score(score: float) -> str:
        if score < 0.25:
            return "LOW"
        if score < 0.50:
            return "MEDIUM"
        if score < 0.75:
            return "HIGH"
        return "CRITICAL"

    @staticmethod
    def _map_status_to_decision(status: str) -> str:
        s = (status or "").strip().upper()
        if s in {"OK", "ALLOW", "SAFE", "GREEN"}:
            return "ALLOW"
        if s in {"WARN", "WARNING", "CAUTION", "YELLOW"}:
            return "WARN"
        if s in {"ERROR"}:
            return "ERROR"
        return "BLOCK"  # deny-by-default

    @staticmethod
    def _thresholds_fingerprint(thresholds: CircuitBreakerThresholds) -> Dict[str, Any]:
        try:
            return dict(vars(thresholds))
        except Exception:
            return {"_": "unavailable"}

    def _error_response(self, request_id: str, reason_code: str, details: Dict[str, Any], latency_ms: int) -> Dict[str, Any]:
        context_hash = canonical_sha256(
            {
                "component": self.COMPONENT,
                "contract_version": self.CONTRACT_VERSION,
                "request_id": str(request_id),
                "reason_code": reason_code,
            }
        )
        return {
            "contract_version": self.CONTRACT_VERSION,
            "component": self.COMPONENT,
            "request_id": str(request_id),
            "context_hash": context_hash,
            "decision": "ERROR",
            "risk": {"score": 0.0, "tier": "LOW"},
            "reason_codes": [reason_code],
            "evidence": {"features": {}, "details": details},
            "meta": {"model_used": False, "latency_ms": int(latency_ms), "fail_closed": True},
        }
