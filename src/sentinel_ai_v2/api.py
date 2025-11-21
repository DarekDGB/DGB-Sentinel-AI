from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .config import CircuitBreakerThresholds, SentinelConfig
from .data_intake import TelemetrySnapshot, normalize_raw_telemetry
from .model_loader import LoadedModel, load_and_verify_model, run_model_inference
from .scoring import SentinelScore, compute_risk_score


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

        # Model is optional – if file or hash not provided, we just skip it.
        self._model: LoadedModel | None = None
        if config.model_path:
            try:
                self._model = load_and_verify_model(
                    model_path=config.model_path,
                    expected_hash=config.model_hash,
                )
            except Exception:
                # In reference implementation we fail open:
                # system still works using non-ML signals.
                self._model = None

    def evaluate_snapshot(self, raw_telemetry: Dict[str, Any]) -> SentinelResult:
        """
        Main entrypoint: evaluate a single telemetry snapshot and
        return a compact result object.
        """
        snapshot: TelemetrySnapshot = normalize_raw_telemetry(raw_telemetry)

        # Map structured telemetry to flat feature dict used by scoring engine.
        features: Dict[str, Any] = {
            "entropy_score": (snapshot.entropy or {}).get("score", 0.0),
            "mempool_score": (snapshot.mempool or {}).get("score", 0.0),
            "reorg_score": (snapshot.reorg or {}).get("score", 0.0),
            "entropy_drop": (snapshot.entropy or {}).get("drop", 0.0),
            "mempool_anomaly": (snapshot.mempool or {}).get("anomaly", 0.0),
            "reorg_depth": (snapshot.reorg or {}).get("depth", 0),
        }

        # Optional ML model contribution.
        if self._model is not None:
            model_score = run_model_inference(self._model, features)
            features["model_score"] = model_score

        sentinel_score: SentinelScore = compute_risk_score(
            features=features,
            thresholds=self._thresholds,
        )

        return SentinelResult(
            status=sentinel_score.status,
            risk_score=sentinel_score.risk_score,
            details=sentinel_score.details,
        )
