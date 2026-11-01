"""Run a bounded, one-shot OpenAQ ingestion and print normalized JSON."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

from .openaq import OpenAQError, fetch_delhi_latest


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch a bounded set of Delhi air-quality observations.")
    parser.add_argument("--max-locations", type=int, default=20, help="Maximum monitor locations to query (1-20).")
    parser.add_argument("--output", help="Optional path for a local JSON snapshot; stdout is used by default.")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAQ_API_KEY", "")
    if not api_key.strip():
        print("Set OPENAQ_API_KEY to an authorized OpenAQ API key.", file=sys.stderr)
        return 2

    try:
        report = fetch_delhi_latest(api_key, max_locations=args.max_locations)
    except (OpenAQError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    payload = {
        "source": "OpenAQ",
        "retrieved_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "measured" if report.observations else "unavailable",
        "locations_seen": report.locations_seen,
        "sensors_seen": report.sensors_seen,
        "rejected_records": report.rejected_records,
        "rejected_by_reason": report.rejected_by_reason,
        "duplicate_records": report.duplicate_records,
        "observations": [observation.to_payload() for observation in report.observations],
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        output_path = Path(args.output)
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"Could not write snapshot: {exc}", file=sys.stderr)
            return 1
        print(f"Saved {len(report.observations)} observations to {output_path}")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
