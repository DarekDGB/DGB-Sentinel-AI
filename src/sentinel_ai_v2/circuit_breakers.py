from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .config import CircuitBreakerThresholds


@dataclass
class CircuitBreakerOutcome:
    """Result of evaluating circuit breakers."""

    triggered: bool
    reasons: list[str]


def evaluate_circuit_breakers(
    features: Dict[str, Any],
    thresholds: CircuitBreakerThresholds,
) -> CircuitBreakerOutcome:
    """
    Evaluate hard-coded emergency rules that override AI decisions.

    If any critical combination is detected, this function returns
    triggered=True and a list of reasons.
    """
    reasons: list[str] = []

    entropy_drop = float(features.get("entropy_drop", 0.0))
    mempool_anomaly = float(features.get("mempool_anomaly", 0.0))
    reorg_depth = int(features.get("reorg_depth", 0))

    if (
        entropy_drop >= thresholds.entropy_drop_threshold
        and mempool_anomaly >= thresholds.mempool_anomaly_threshold
        and reorg_depth >= thresholds.reorg_depth_threshold
    ):
        reasons.append("combo: entropy + mempool + reorg")

    triggered = len(reasons) > 0
    return CircuitBreakerOutcome(triggered=triggered, reasons=reasons)
