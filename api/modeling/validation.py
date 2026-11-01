"""Spatial holdout evaluation helpers; metrics are data-dependent outputs."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Sequence

from ..schemas import Observation


@dataclass(frozen=True)
class RegressionMetrics:
    sample_count: int
    mae: float
    rmse: float
    bias: float


@dataclass(frozen=True)
class LeaveOneStationOutReport:
    metrics: RegressionMetrics | None
    skipped_predictions: int
    held_out_stations: int


def regression_metrics(pairs: Sequence[tuple[float, float]]) -> RegressionMetrics | None:
    """Compute MAE, RMSE, and mean(prediction - actual); no pairs => None."""
    if not pairs:
        return None
    errors: list[float] = []
    for actual, predicted in pairs:
        if not math.isfinite(actual) or not math.isfinite(predicted):
            raise ValueError("Validation values must be finite.")
        errors.append(predicted - actual)
    count = len(errors)
    return RegressionMetrics(
        sample_count=count,
        mae=sum(abs(error) for error in errors) / count,
        rmse=math.sqrt(sum(error * error for error in errors) / count),
        bias=sum(errors) / count,
    )


def leave_one_station_out(
    observations: Sequence[Observation],
    predict: Callable[[Sequence[Observation], Observation], float | None],
) -> LeaveOneStationOutReport:
    """Evaluate by withholding every reading from each station in turn.

    The caller's predictor must apply pollutant, unit, time, and spatial
    support rules. No accuracy claim is produced when no held-out prediction
    could be made.
    """
    measured = [observation for observation in observations if observation.status == "measured"]
    stations = sorted({observation.station.id for observation in measured})
    pairs: list[tuple[float, float]] = []
    skipped = 0

    for station_id in stations:
        training = [item for item in measured if item.station.id != station_id]
        held_out = [item for item in measured if item.station.id == station_id]
        for target in held_out:
            predicted = predict(training, target)
            if predicted is None:
                skipped += 1
                continue
            pairs.append((target.value, predicted))

    return LeaveOneStationOutReport(
        metrics=regression_metrics(pairs),
        skipped_predictions=skipped,
        held_out_stations=len(stations),
    )
