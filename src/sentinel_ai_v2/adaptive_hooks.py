# src/sentinel_ai_v2/adaptive_hooks.py

from __future__ import annotations

from typing import Any, Optional

from .adaptive_core_bridge import SentinelAdaptiveCoreBridge


def report_reorg_anomaly_to_adaptive(
    block_height: int,
    score: float,
    details: Optional[dict[str, Any]] = None,
    bridge: Optional[SentinelAdaptiveCoreBridge] = None,
) -> None:
    """
    Helper used by Sentinel AI v2 when it detects a suspicious reorg pattern.

    This function converts Sentinel's internal detection signal into a
    unified ThreatPacket and sends it (via SentinelAdaptiveCoreBridge)
    to the DigiByte Quantum Adaptive Core, if available.

    Parameters:
        block_height:
            Height at which the suspicious reorg / fork behaviour occurred.

        score:
            A float in [0.0, 1.0] representing how severe/likely the anomaly is.
            This will be converted to a severity level in [0, 10].

        details:
            Optional dict with extra context (window size, peers, etc.).

        bridge:
            Optional existing SentinelAdaptiveCoreBridge instance.
            If None, a new bridge will be created internally.
    """
    # If no bridge passed, create a default one (will be no-op if Adaptive Core
    # isn't available in this environment).
    bridge = bridge or SentinelAdaptiveCoreBridge()

    if not bridge.is_available:
        # Adaptive Core not present → do nothing, don't break Sentinel.
        return

    # Map score [0.0, 1.0] → severity [0, 10]
    raw_severity = int(round(score * 10))
    severity = max(0, min(10, raw_severity))

    metadata: dict[str, Any] = {"score": score}
    if details:
        metadata.update(details)

    bridge.submit_simple_threat(
        source_layer="sentinel_ai_v2",
        threat_type="reorg_pattern",
        severity=severity,
        description="Suspicious reorg pattern detected by Sentinel AI v2.",
        block_height=block_height,
        metadata=metadata,
    )
