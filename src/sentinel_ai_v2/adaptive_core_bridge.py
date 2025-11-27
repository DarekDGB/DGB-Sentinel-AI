# src/sentinel_ai_v2/adaptive_core_bridge.py

from __future__ import annotations

from typing import Any, Optional

try:
    # These imports will only work when the Adaptive Core package
    # is available in the same environment. If not, we handle it
    # gracefully and keep Sentinel AI v2 fully functional.
    from adaptive_core.interface import AdaptiveCoreInterface  # type: ignore
    from adaptive_core.threat_packet import ThreatPacket  # type: ignore
except ImportError:  # pragma: no cover - optional integration
    AdaptiveCoreInterface = None  # type: ignore
    ThreatPacket = None  # type: ignore


class SentinelAdaptiveCoreBridge:
    """
    Optional bridge between Sentinel AI v2 and the DigiByte Quantum
    Adaptive Core.

    Design goals:
      - Do NOT break Sentinel AI v2 if the adaptive_core package
        is not installed.
      - When adaptive_core *is* available, allow Sentinel to:
          * submit ThreatPacket objects to the Adaptive Core
          * submit feedback labels (TRUE_POSITIVE, FALSE_POSITIVE, MISSED_ATTACK)
          * request immune reports

    This keeps Sentinel "adaptive-ready" without introducing a hard
    runtime dependency.
    """

    def __init__(self, interface: Optional["AdaptiveCoreInterface"] = None) -> None:
        # If AdaptiveCoreInterface is not available, this bridge becomes
        # a no-op and Sentinel can still run normally.
        if AdaptiveCoreInterface is None:
            self._available = False
            self._interface = None
        else:
            self._available = True
            self._interface = interface or AdaptiveCoreInterface()

    @property
    def is_available(self) -> bool:
        """
        Returns True if the adaptive_core integration is available
        in the current environment.
        """
        return self._available and self._interface is not None

    # ------------------------------------------------------------------ #
    # Threat submission
    # ------------------------------------------------------------------ #

    def submit_simple_threat(
        self,
        source_layer: str,
        threat_type: str,
        severity: int,
        description: str,
        *,
        node_id: Optional[str] = None,
        wallet_id: Optional[str] = None,
        tx_id: Optional[str] = None,
        block_height: Optional[int] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Convenience helper for Sentinel to send a basic threat signal
        into the Adaptive Core.
        """
        if not self.is_available:
            # Adaptive Core is not installed / wired in this environment.
            # We silently no-op to avoid breaking Sentinel.
            return

        assert ThreatPacket is not None  # for type checkers

        packet = ThreatPacket(
            source_layer=source_layer,
            threat_type=threat_type,
            severity=severity,
            description=description,
            node_id=node_id,
            wallet_id=wallet_id,
            tx_id=tx_id,
            block_height=block_height,
            metadata=metadata,
        )

        self._interface.submit_threat_packet(packet)  # type: ignore[arg-type]

    # ------------------------------------------------------------------ #
    # Feedback submission (teaching the Adaptive Core)
    # ------------------------------------------------------------------ #

    def submit_feedback_label(
        self,
        *,
        layer: str,
        feedback: str,
        event_id: str,
    ) -> None:
        """
        Submit a single labelled feedback event to the Adaptive Core.

        `feedback` should be one of:
          - "TRUE_POSITIVE"
          - "FALSE_POSITIVE"
          - "MISSED_ATTACK"

        (case-insensitive — it will be normalised inside the core).

        We intentionally send a very lightweight object with attributes
        (event_id, layer, feedback). The Adaptive Core's learning logic
        only needs these fields and accepts both enums and string tags.
        """

        if not self.is_available:
            # No Adaptive Core present → do nothing.
            return

        # Define a tiny lightweight feedback object that matches what the
        # AdaptiveEngine expects (duck-typing).
        class _FeedbackEvent:
            def __init__(self, event_id: str, layer: str, feedback: str) -> None:
                self.event_id = event_id
                self.layer = layer
                self.feedback = feedback

        # Normalise feedback tag to upper-case; the core will accept strings.
        tag = feedback.upper()

        events = [_FeedbackEvent(event_id=event_id, layer=layer, feedback=tag)]

        # The AdaptiveCoreInterface already exposes submit_feedback_events,
        # which forwards the iterable of events into the AdaptiveEngine.
        self._interface.submit_feedback_events(events)  # type: ignore[arg-type]

    # ------------------------------------------------------------------ #
    # Read-only views
    # ------------------------------------------------------------------ #

    def get_immune_report_text(self, min_severity: int = 0) -> str:
        """
        Optional helper for Sentinel to fetch a human-readable immune report
        for logging or debugging, when the Adaptive Core is available.
        """
        if not self.is_available:
            return "Adaptive Core integration not available in this environment."

        return self._interface.get_immune_report_text(min_severity=min_severity)
