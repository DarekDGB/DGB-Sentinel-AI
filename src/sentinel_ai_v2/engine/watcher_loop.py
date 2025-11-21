from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Optional

from ..api import SentinelClient, SentinelResult
from ..config import load_config


TelemetrySource = Iterable[Dict[str, Any]]
ResultHandler = Callable[[SentinelResult], None]


def build_default_client() -> SentinelClient:
    """
    Convenience helper: build a SentinelClient using the default config
    loader. ADN or node operators can instead construct their own clients.
    """
    cfg = load_config()
    return SentinelClient(config=cfg)


def default_print_handler(result: SentinelResult) -> None:
    """
    Default handler used if caller does not supply one.

    Simply prints a one-line summary, suitable for debugging or basic logs.
    """
    print(
        f"[SentinelAI v2] status={result.status} "
        f"score={result.risk_score:.3f} "
        f"details={','.join(result.details)}"
    )


def watch_stream(
    source: TelemetrySource,
    client: Optional[SentinelClient] = None,
    handler: Optional[ResultHandler] = None,
) -> None:
    """
    Consume a stream of telemetry snapshots and feed them through Sentinel AI v2.

    - `source`  – iterable of dict telemetry snapshots
    - `client`  – optional pre-configured SentinelClient
    - `handler` – optional callback to process each SentinelResult
    """
    if client is None:
        client = build_default_client()
    if handler is None:
        handler = default_print_handler

    for snapshot in source:
        result = client.evaluate_snapshot(snapshot)
        handler(result)
