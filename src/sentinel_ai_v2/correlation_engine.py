from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class CorrelationResult:
    """Represents the outcome of multi-signal correlation."""

    base_score: float
    adjusted_score: float
    details: list[str]


def correlate_signals(features: Dict[str, Any]) -> CorrelationResult:
    """
    Combine multiple input features into a base risk score.

    This is a placeholder for a graph-based / multi-signal correlation model.
    For now it simply aggregates a few numeric hints if present.
    """
    details: list[str] = []
    base = 0.0

    entropy_score = float(features.get("entropy_score", 0.0))
    mempool_score = float(features.get("mempool_score", 0.0))
    reorg_score = float(features.get("reorg_score", 0.0))

    if entropy_score:
        base += entropy_score
        details.append(f"entropy_score={entropy_score}")
    if mempool_score:
        base += mempool_score
        details.append(f"mempool_score={mempool_score}")
    if reorg_score:
        base += reorg_score
        details.append(f"reorg_score={reorg_score}")

    # Normalise to [0, 1]
    adjusted = max(0.0, min(base, 1.0))

    return CorrelationResult(
        base_score=base,
        adjusted_score=adjusted,
        details=details
    )
