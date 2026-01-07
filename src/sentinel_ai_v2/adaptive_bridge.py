"""
Adaptive bridge helpers for Sentinel-AI v2.

This module does NOT change Sentinel's detection logic.
It only provides small helpers to turn anomalies into
AdaptiveEvent objects and a placeholder "emit" function.

Later, DigiByte-Quantum-Adaptive-Core can plug into this.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional

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
        logger.debug("AdaptiveEvent %s", json.dumps(payload, sort_keys=True, default=str))
    except Exception as e:  # pragma: no cover – defensive
        logger.error("Failed to log AdaptiveEvent: %s", e)


def export_to_adaptive_core(event: AdaptiveEvent) -> None:
    """
    Alias kept for integration readability.

    Today this simply calls emit_adaptive_event().
    Later this can become the single integration point for
    Adaptive Core transports (HTTP/gRPC/queue/etc).
    """
    emit_adaptive_event(event)


def emit_adaptive_event_from_signal(
    *,
    signal_name: str,
    severity: float,
    qri_delta: float = 0.0,
    layer: str = "sentinel",
    context: Dict[str, Any] | None = None,
) -> None:
    """
    Convenience helper: take any Sentinel signal name and push it
    into the Adaptive Core.

    This keeps the calling code very small:

        emit_adaptive_event_from_signal(
            signal_name="entropy_drop",
            severity=0.82,
            qri_delta=-0.15,
            context={"window": "30s", "chain": "DigiByte"},
        )

    Notes:
    - This does NOT alter Sentinel detection logic.
    - This is a bridge that maps a signal into a structured AdaptiveEvent.
    """
    ctx = dict(context or {})
    ctx.setdefault("signal_name", signal_name)
    ctx.setdefault("qri_delta", float(qri_delta))

    evt = build_adaptive_event(
        anomaly_type=signal_name,
        severity="HIGH" if float(severity) >= 0.75 else "MEDIUM" if float(severity) >= 0.4 else "LOW",
        qri_score=float(severity),
        source="sentinel_signal",
        metadata=ctx,
    )

    # If caller overrides layer, respect it.
    # (We keep build_adaptive_event layer default "sentinel" to keep v2 stable.)
    try:
        evt.layer = layer  # type: ignore[attr-defined]
    except Exception:
        # If AdaptiveEvent is frozen/immutable, we just keep default.
        pass

    export_to_adaptive_core(evt)
