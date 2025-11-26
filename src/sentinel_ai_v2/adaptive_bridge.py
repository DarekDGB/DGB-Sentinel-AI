"""
Adaptive bridge helpers for Sentinel-AI v2.

This module does NOT change Sentinel's detection logic.
It only provides small helpers to turn anomalies into
AdaptiveEvent objects and a placeholder "emit" function.

Later, DigiByte-Quantum-Adaptive-Core can plug into this.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Optional
import json
import logging
from datetime import datetime, timezone

from .adaptive_event import AdaptiveEvent

logger = logging.getLogger(__name__)


def build_adaptive_event(
    *,
    anomaly_type: str,
    severity: str,
    qri_score: float,
    source: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> AdaptiveEvent:
    """
    Factory helper to construct a normalized AdaptiveEvent
    from Sentinel anomaly data.

    This keeps the Sentinel → Adaptive Core interface clean:
    Sentinel passes only basic fields, Adaptive Core can
    evolve independently.
    """
    return AdaptiveEvent(
        layer="sentinel",
        anomaly_type=anomaly_type,
        severity=severity,
        qri_score=qri_score,
        source=source,
        metadata=metadata or {},
        ts=datetime.now(timezone.utc),
    )


def emit_adaptive_event(event: AdaptiveEvent) -> None:
    """
    Placeholder sink for AdaptiveEvents.

    For v2 this only logs a structured JSON line.
    Later, DigiByte-Quantum-Adaptive-Core can replace
    this with:
      – HTTP/gRPC send
      – message queue push
      – file / DB logger, etc.
    """
    try:
        payload = asdict(event)
        logger.debug("AdaptiveEvent %s", json.dumps(payload, sort_keys=True))
    except Exception as e:  # pragma: no cover – defensive
        logger.error("Failed to log AdaptiveEvent: %s", e)
