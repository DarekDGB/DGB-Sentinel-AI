from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class CircuitBreakerThresholds:
    """Static thresholds for hard-coded circuit breakers."""

    entropy_drop_threshold: float = 0.2
    mempool_anomaly_threshold: float = 0.7
    reorg_depth_threshold: int = 3
    multi_signal_window_seconds: int = 60


@dataclass
class SentinelConfig:
    """Configuration object for Sentinel AI v2."""

    model_path: str = "models/sentinel_v2.onnx"
    model_hash: str | None = None
    model_signature_path: str | None = None

    circuit_breakers: CircuitBreakerThresholds = field(
        default_factory=CircuitBreakerThresholds
    )

    enabled_detectors: Dict[str, bool] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)


def load_config(path: str | None = None) -> SentinelConfig:
    """
    Load configuration from a file.

    For now this returns a default config object. In a real implementation
    this should parse YAML/JSON and validate the structure.
    """
    # Placeholder: we keep it simple and safe for now.
    _ = path
    return SentinelConfig()
