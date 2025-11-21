from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .model_loader import load_model
from .adversarial_engine import compute_adversarial_score
from .correlation_engine import compute_correlation_anomaly
from .circuit_breakers import evaluate_circuit_breakers
from .config import ScoreWeights, CircuitBreakerThresholds


@dataclass
class ScoreResult:
    """Final output of the Sentinel-AI v2 scoring engine."""

    level: str
    score: float
    reasons: list[str]


class SentinelScoringEngine:
    """
    Main end-to-end scoring pipeline combining:
    - Adversarial features
    - Correlation anomaly
    - ML model predictive score
    - Circuit breakers (override)
    """

    def __init__(
        self,
        model_path: str,
        weights: ScoreWeights,
        cb_thresholds: CircuitBreakerThresholds,
    ) -> None:
        self.model = load_model(model_path)
        self.weights = weights
        self.cb_thresholds = cb_thresholds

    def _determine_level(self, score: float) -> str:
        if score >= 0.85:
            return "CRITICAL"
        if score >= 0.65:
            return "HIGH"
        if score >= 0.40:
            return "ELEVATED"
        return "NORMAL"

    def evaluate(self, features: Dict[str, Any]) -> ScoreResult:
        reasons: list[str] = []

        # 1) circuit breakers first
        cb = evaluate_circuit_breakers(features, self.cb_thresholds)
        if cb.triggered:
            return ScoreResult(
                level="CRITICAL",
                score=1.0,
                reasons=["circuit_breaker"] + cb.reasons,
            )

        # 2) compute partial metrics
        adv_score = compute_adversarial_score(features)
        corr_score = compute_correlation_anomaly(features)
        ml_score = float(self.model.predict(features))  # type: ignore

        # 3) weighted final score
        final_score = (
            adv_score * self.weights.adversarial_weight
            + corr_score * self.weights.correlation_weight
            + ml_score * self.weights.model_weight
        )

        # 4) choose level
        level = self._determine_level(final_score)

        # 5) collect reasons
        reasons.append(f"adv={adv_score:.2f}")
        reasons.append(f"corr={corr_score:.2f}")
        reasons.append(f"ml={ml_score:.2f}")

        return ScoreResult(
            level=level,
            score=final_score,
            reasons=reasons,
        )
