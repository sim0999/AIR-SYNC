"""Run leave-one-station-out IDW evaluation on a saved observation snapshot."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import timedelta, datetime, timezone
import json
import math
from pathlib import Path
import sys
from typing import Sequence

from ..schemas import Observation
from .idw import MAX_IDW_POWER, estimate_idw
from .validation import leave_one_station_out


def _load_observations(path: Path) -> list[Observation]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read observation snapshot: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("observations"), list):
        raise ValueError("Snapshot must be an object containing an observations list.")
    try:
        return [Observation.model_validate(item) for item in payload["observations"]]
    except Exception as exc:
        raise ValueError(f"Snapshot contains an invalid observation record: {exc}") from exc


def _evaluate_group(
    records: Sequence[Observation],
    *,
    max_age: timedelta,
    max_time_spread: timedelta,
    support_radius_km: float,
    power: float,
) -> dict[str, object]:
    def predict(training: Sequence[Observation], target: Observation) -> float | None:
        estimate = estimate_idw(
            training,
            target_latitude=target.station.latitude,
            target_longitude=target.station.longitude,
            pollutant=target.pollutant,
            as_of=target.observed_at,
            max_observation_age=max_age,
            max_time_spread=max_time_spread,
            max_support_radius_km=support_radius_km,
            minimum_stations=3,
            power=power,
        )
        return estimate.value if estimate else None

    report = leave_one_station_out(records, predict)
    return {
        "status": "evaluated" if report.metrics else "unavailable",
        "sample_count": report.metrics.sample_count if report.metrics else 0,
        "held_out_stations": report.held_out_stations,
        "skipped_predictions": report.skipped_predictions,
        "metrics": (
            {
                "mae": report.metrics.mae,
                "rmse": report.metrics.rmse,
                "bias_prediction_minus_actual": report.metrics.bias,
            }
            if report.metrics
            else None
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate IDW with leave-one-station-out validation on saved observations."
    )
    parser.add_argument("snapshot", type=Path, help="Path to an OpenAQ JSON snapshot.")
    parser.add_argument("--max-age-minutes", type=float, required=True)
    parser.add_argument("--max-time-spread-minutes", type=float, required=True)
    parser.add_argument("--support-radius-km", type=float, required=True)
    parser.add_argument("--power", type=float, default=2.0)
    args = parser.parse_args()

    for name in ("max_age_minutes", "max_time_spread_minutes", "support_radius_km", "power"):
        value = getattr(args, name)
        if not math.isfinite(value):
            parser.error(f"--{name.replace('_', '-')} must be finite")
    if args.max_age_minutes <= 0 or args.max_time_spread_minutes < 0:
        parser.error("freshness must be positive and time spread cannot be negative")
    if args.support_radius_km <= 0 or not 0 < args.power <= MAX_IDW_POWER:
        parser.error(f"support radius must be positive and IDW power must be in (0, {MAX_IDW_POWER:g}]")

    try:
        observations = _load_observations(args.snapshot)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    groups: dict[tuple[str, str], list[Observation]] = defaultdict(list)
    for observation in observations:
        if observation.status == "measured":
            groups[(observation.pollutant, observation.unit)].append(observation)

    results = [
        {
            "pollutant": pollutant,
            "unit": unit,
            **_evaluate_group(
                records,
                max_age=timedelta(minutes=args.max_age_minutes),
                max_time_spread=timedelta(minutes=args.max_time_spread_minutes),
                support_radius_km=args.support_radius_km,
                power=args.power,
            ),
        }
        for (pollutant, unit), records in sorted(groups.items())
    ]
    output = {
        "status": "evaluated" if any(group["status"] == "evaluated" for group in results) else "unavailable",
        "method": f"inverse_distance_weighting(power={args.power:g})",
        "validation": "leave_one_station_out",
        "snapshot": str(args.snapshot),
        "evaluated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "settings": {
            "maximum_observation_age_minutes": args.max_age_minutes,
            "maximum_timestamp_spread_minutes": args.max_time_spread_minutes,
            "support_radius_km": args.support_radius_km,
            "minimum_support_stations": 3,
        },
        "groups": results,
        "notice": "Metrics describe only this snapshot and these settings; they are not a general accuracy guarantee.",
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
