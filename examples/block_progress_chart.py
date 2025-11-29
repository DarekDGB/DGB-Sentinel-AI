"""
Block Progress Chart

Reads block_progress_log.jsonl (created by block_progress_recorder.py)
and draws a simple chart of block height over time, marking stalled
periods if any.

Requires matplotlib:
    pip install matplotlib
"""

import json
from datetime import datetime

import matplotlib.pyplot as plt  # noqa: E402


LOG_FILE = "block_progress_log.jsonl"


def load_log(path: str):
    timestamps = []
    heights = []
    statuses = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            timestamps.append(datetime.fromisoformat(entry["timestamp"]))
            heights.append(entry["current_height"])
            statuses.append(entry["status"])

    return timestamps, heights, statuses


def main() -> None:
    ts, heights, statuses = load_log(LOG_FILE)

    if not ts:
        print("No log data found. Run block_progress_recorder.py first.")
        return

    plt.figure()
    plt.plot(ts, heights, marker=".", linewidth=1)

    plt.xlabel("Time")
    plt.ylabel("Block height")
    plt.title("DigiByte Block Progress (Sentinel AI v2)")

    # Optional: highlight stalled samples in red
    stalled_ts = [t for t, s in zip(ts, statuses) if s == "stalled"]
    stalled_h = [h for h, s in zip(heights, statuses) if s == "stalled"]
    if stalled_ts:
        plt.scatter(stalled_ts, stalled_h)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
