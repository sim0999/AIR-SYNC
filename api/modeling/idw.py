"""Explainable inverse-distance-weighted baseline.

This helper is deliberately not wired to an API route. Callers must supply
freshness, temporal-alignment, support-radius, and minimum-station settings;
estimates are unavailable when those conditions are not met.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import math
from typing import Sequence

from ..schemas import Observation


EARTH_RADIUS_KM = 6371.0088
MAX_IDW_POWER = 8.0


@dataclass(frozen=True)
class IDWEstimate:
    value: float
    unit: str
    pollutant: str
    method: str
    support_station_ids: tuple[str, ...]
    support_count: int
    nearest_distance_km: float
    farthest_distance_km: float
    support_radius_km: float
    observation_time_span_seconds: float


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    haversine = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(min(1.0, haversine)))


def estimate_idw(
    observations: Sequence[Observation],
    *,
    target_latitude: float,
    target_longitude: float,
    pollutant: str,
    as_of: datetime,
    max_observation_age: timedelta,
    max_time_spread: timedelta,
    max_support_radius_km: float,
    minimum_stations: int = 3,
    power: float = 2.0,
) -> IDWEstimate | None:
    """Estimate a value from comparable measured observations, or return None.

    Observations must be measured, match the requested pollutant and unit,
    fall inside the caller-specified freshness window and support radius, and
    have a mutually acceptable timestamp span. Each station contributes at
    most its most recent reading for this query. An exact station match is
    not an estimate and returns None.
    """
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("as_of must include a timezone.")
    if (
        not math.isfinite(target_latitude)
        or not math.isfinite(target_longitude)
        or not -90 <= target_latitude <= 90
        or not -180 <= target_longitude <= 180
    ):
        raise ValueError("Target coordinates must be valid WGS 84 latitude/longitude values.")
    if max_observation_age <= timedelta(0) or max_time_spread < timedelta(0):
        raise ValueError("Freshness and time-spread limits must be nonnegative, and freshness must be positive.")
    if not math.isfinite(max_support_radius_km) or max_support_radius_km <= 0:
        raise ValueError("max_support_radius_km must be finite and greater than zero.")
    if not math.isfinite(power) or not 0 < power <= MAX_IDW_POWER:
        raise ValueError(f"power must be finite and in the range (0, {MAX_IDW_POWER:g}].")
    if minimum_stations < 2:
        raise ValueError("minimum_stations must be at least two.")

    target_time = as_of.astimezone(timezone.utc)
    requested_pollutant = pollutant.strip().casefold()
    latest_by_station: dict[str, tuple[Observation, datetime]] = {}
    expected_unit: str | None = None

    for observation in observations:
        if observation.status != "measured" or observation.pollutant.strip().casefold() != requested_pollutant:
            continue
        observed_time = observation.observed_at.astimezone(timezone.utc)
        age = target_time - observed_time
        if age < timedelta(0) or age > max_observation_age:
            continue
        if expected_unit is None:
            expected_unit = observation.unit
        if observation.unit != expected_unit:
            return None
        current = latest_by_station.get(observation.station.id)
        if current is None or observed_time > current[1]:
            latest_by_station[observation.station.id] = (observation, observed_time)

    if len(latest_by_station) < minimum_stations:
        return None

    support: list[tuple[Observation, float]] = []
    for observation, _ in latest_by_station.values():
        distance = _haversine_km(
            target_latitude,
            target_longitude,
            observation.station.latitude,
            observation.station.longitude,
        )
        if distance < 0.001:
            return None
        if distance <= max_support_radius_km:
            support.append((observation, distance))

    if len(support) < minimum_stations:
        return None

    support_times = [latest_by_station[observation.station.id][1] for observation, _ in support]
    time_span = max(support_times) - min(support_times)
    if time_span > max_time_spread:
        return None

    weighted_sum = 0.0
    weight_total = 0.0
    for observation, distance in support:
        weight = distance ** (-power)
        weighted_sum += observation.value * weight
        weight_total += weight

    if not math.isfinite(weight_total) or weight_total <= 0:
        return None
    estimated_value = weighted_sum / weight_total
    if not math.isfinite(estimated_value):
        return None

    distances = [distance for _, distance in support]
    return IDWEstimate(
        value=estimated_value,
        unit=support[0][0].unit,
        pollutant=support[0][0].pollutant,
        method=f"inverse_distance_weighting(power={power:g})",
        support_station_ids=tuple(sorted(observation.station.id for observation, _ in support)),
        support_count=len(support),
        nearest_distance_km=min(distances),
        farthest_distance_km=max(distances),
        support_radius_km=max_support_radius_km,
        observation_time_span_seconds=time_span.total_seconds(),
    )
