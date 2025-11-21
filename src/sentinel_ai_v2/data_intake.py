from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class TelemetrySnapshot:
    """
    Container for a single telemetry snapshot.

    All fields are generic dictionaries to keep this reference implementation
    chain-agnostic. Real deployments can define stricter schemas.
    """

    entropy: Dict[str, Any] | None = None
    mempool: Dict[str, Any] | None = None
    reorg: Dict[str, Any] | None = None
    peers: Dict[str, Any] | None = None
    hashrate: Dict[str, Any] | None = None
    wallet_signals: Dict[str, Any] | None = None
    extra: Dict[str, Any] | None = None


def normalize_raw_telemetry(raw: Dict[str, Any]) -> TelemetrySnapshot:
    """
    Convert a raw telemetry dictionary (from DQSN / node / external service)
    into a structured TelemetrySnapshot.
    """
    return TelemetrySnapshot(
        entropy=raw.get("entropy"),
        mempool=raw.get("mempool"),
        reorg=raw.get("reorg"),
        peers=raw.get("peers"),
        hashrate=raw.get("hashrate"),
        wallet_signals=raw.get("wallet_signals"),
        extra=raw.get("extra"),
    )
