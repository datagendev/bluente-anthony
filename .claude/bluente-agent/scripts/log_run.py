#!/usr/bin/env python3
"""
Log a bluente-agent pipeline run.

Usage:
    echo '{"run_id": "abc", ...}' | python log_run.py [--output-dir ./runs]

Reads run metadata JSON from stdin and writes to runs/{run_id}.json.
Appends a summary line to runs/index.csv.
"""

import json
import sys
import os
import csv
import uuid
from datetime import datetime, timezone

INDEX_HEADERS = [
    "run_id", "timestamp", "trigger_mode", "signals_scanned",
    "signals_qualified", "leads_delivered", "pipeline_status",
]


def generate_run_id() -> str:
    return str(uuid.uuid4())[:8]


def create_run_log(data: dict, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    run_id = data.get("run_id") or generate_run_id()
    data["run_id"] = run_id
    if "timestamp" not in data:
        data["timestamp"] = datetime.now(timezone.utc).isoformat()

    run_path = os.path.join(output_dir, f"{run_id}.json")
    with open(run_path, "w") as f:
        json.dump(data, f, indent=2)

    index_path = os.path.join(output_dir, "index.csv")
    write_header = not os.path.exists(index_path)
    with open(index_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=INDEX_HEADERS, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerow({h: data.get(h, "") for h in INDEX_HEADERS})

    return run_id


def main():
    output_dir = "./runs"
    args = sys.argv[1:]
    if "--output-dir" in args:
        idx = args.index("--output-dir")
        if idx + 1 < len(args):
            output_dir = args[idx + 1]

    if sys.stdin.isatty():
        print("Usage: echo '{...}' | python log_run.py [--output-dir ./runs]")
        sys.exit(1)

    data = json.load(sys.stdin)
    run_id = create_run_log(data, output_dir)
    print(f"Logged run {run_id} -> {output_dir}/{run_id}.json")


if __name__ == "__main__":
    main()
