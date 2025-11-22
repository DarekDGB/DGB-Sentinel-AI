from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from .wrapper.sentinel_wrapper import SentinelWrapper


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sentinel-ai",
        description="Sentinel AI v2 – Quantum-Resistant Threat Engine for DigiByte",
    )

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        required=True,
    )

    # sentinel-ai snapshot --file telemetry.json --pretty
    snapshot = subparsers.add_parser(
        "snapshot",
        help="Evaluate a single telemetry snapshot (JSON) and print risk result.",
    )
    snapshot.add_argument(
        "-f",
        "--file",
        metavar="PATH",
        help="Path to JSON file with telemetry. If omitted or '-', read from stdin.",
        default="-",
    )
    snapshot.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )

    # sentinel-ai version
    subparsers.add_parser(
        "version",
        help="Print Sentinel AI v2 version information.",
    )

    return parser


def _load_snapshot(path: str) -> Dict[str, Any]:
    """
    Load telemetry snapshot from a file or stdin.
    Expected format: JSON object.
    """
    if path == "-" or path.strip() == "":
        raw = sys.stdin.read()
    else:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[sentinel-ai] Invalid JSON input: {exc}") from exc

    if not isinstance(data, dict):
        raise SystemExit("[sentinel-ai] Telemetry JSON must be a single object (dict).")

    return data


def _cmd_snapshot(args: argparse.Namespace) -> int:
    wrapper = SentinelWrapper()
    snapshot = _load_snapshot(args.file)
    result = wrapper.evaluate(snapshot)

    output = {
        "status": result.status,
        "risk_score": result.risk_score,
        "details": result.details,
    }

    if args.pretty:
        json.dump(output, sys.stdout, indent=2)
    else:
        json.dump(output, sys.stdout)

    sys.stdout.write("\n")
    return 0


def _cmd_version() -> int:
    # Trzymamy wersję tutaj, żeby dev mógł to łatwo podmienić.
    version_info = {
        "sentinel_ai_v2": "0.1.0",
        "description": "Quantum-Resistant Threat Engine for DigiByte",
    }
    json.dump(version_info, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "snapshot":
        return _cmd_snapshot(args)
    if args.command == "version":
        return _cmd_version()

    parser.error(f"Unknown command: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
