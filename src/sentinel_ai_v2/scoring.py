from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .adversarial_engine import analyse_for_adversarial_patterns
from .circuit_breakers import CircuitBreakerOutcome, evaluate_circuit_breakers
from .config import CircuitBreakerThresholds
from .correlation_engine import CorrelationResult, correlate_signals


@dataclass
class SentinelScore:
    """Final aggregated risk score for a single telemetry snapshot."""

    status: str
    risk_score: float
    details: list[str]
    circuit_breakers: CircuitBreakerOutcome
    correlation: CorrelationResult


def compute_risk_score(
    features: Dict[str, Any],
    thresholds: CircuitBreakerThresholds,
) -> SentinelScore:
    """
    Orchestrate correlation, adversarial analysis and circuit breakers
    to produce a final risk status.

    `features` is a flat dict with numeric hints like:
      - entropy_score
      - mempool_score
      - reorg_score
      - entropy_drop
      - mempool_anomaly
      - reorg_depth
      - model_score (optional, from offline AI model)
    """
    # 1) multi-signal correlation
    correlation = correlate_signals(features)

    # 2) adversarial heuristics
    adv = analyse_for_adversarial_patterns(features)

    # 3) circuit breakers (can override everything)
    cb = evaluate_circuit_breakers(features, thresholds)

    # 4) base score from correlation + adversarial boost
    score = correlation.adjusted_score + adv.risk_boost
    score = max(0.0, min(score, 1.0))

    # 5) if circuit breaker fired → force CRITICAL
    if cb.triggered:
        status = "CRITICAL"
        score = max(score, 0.99)
    elif score >= 0.8:
        status = "HIGH"
    elif score >= 0.4:
        status = "ELEVATED"
    else:
        status = "NORMAL"

    details = list(correlation.details)
    if adv.reasons:
        details.extend([f"adversarial:{r}" for r in adv.reasons])
    if cb.reasons:
        details.extend([f"circuit_breaker:{r}" for r in cb.reasons])

    return SentinelScore(
        status=status,
        risk_score=score,
        details=details,
        circuit_breakers=cb,
        correlation=correlation,
    )
