"""
Block Progress Recorder

Periodically calls the BlockProgressMonitor and appends results
to a JSONL file (one JSON object per line).

This script is OPTIONAL and provided as an example of how
Sentinel AI v2 can feed dashboards.
"""

import json
import logging
import time
from datetime import datetime

from sentinel_ai_v2.telemetry_monitor import (
    init_block_progress_monitor,
    check_block_progress,
)
from sentinel_ai_v2.rpc_client import SimpleRpcClient

logging.basicConfig(level=logging.INFO)

# TODO: adjust these to your actual node RPC settings
RPC_URL = "http://127.0.0.1:14022"
RPC_USER = "user"
RPC_PASS = "pass"

LOG_FILE = "block_progress_log.jsonl"
INTERVAL_SECONDS = 60  # how often to sample


def status_to_dict(status) -> dict:
    return {
        "timestamp": status.timestamp.isoformat(),
        "current_height": status.current_height,
        "previous_height": status.previous_height,
        "status": status.status,
        "stalled_for_seconds": status.stalled_for_seconds,
    }


def main() -> None:
    rpc = SimpleRpcClient(RPC_URL, RPC_USER, RPC_PASS)
    init_block_progress_monitor(rpc, stall_threshold_seconds=600)

    while True:
        status = check_block_progress()
        logging.info("Status: %s", status)

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(status_to_dict(status)) + "\n")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    print(f"[{datetime.utcnow().isoformat()}] Block progress recorder started.")
    main()
