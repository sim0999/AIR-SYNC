"""OpenAQ v3 adapter with provenance-preserving normalization.

This module does not start network traffic at import time. Calls require an
explicit API key and should be enabled only after the project's data-use and
frontend contract decisions are complete.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import json
import math
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ..schemas import Observation as ObservationSchema


OPENAQ_API_ROOT = "https://api.openaq.org/v3"
DELHI_CENTER_LATITUDE = 28.6139
DELHI_CENTER_LONGITUDE = 77.2090
DELHI_SEARCH_RADIUS_METERS = 25_000
FUTURE_TIMESTAMP_TOLERANCE = timedelta(minutes=5)


class OpenAQError(RuntimeError):
    """Raised when OpenAQ cannot provide a usable response."""


class OpenAQAuthenticationError(OpenAQError):
    """Raised when OpenAQ rejects the configured API key."""


class OpenAQRateLimitError(OpenAQError):
    """Raised when OpenAQ asks the client to slow down."""

    def __init__(self, message: str, retry_after: str | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


@dataclass(frozen=True)
class Observation:
    """A normalized measured value with its source and station provenance."""

    status: str
    pollutant: str
    value: float
    unit: str
    observed_at: str
    source: str
    provider: str | None
    station_id: str
    station_name: str
    latitude: float
    longitude: float
    sensor_id: str
    attribution: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    coverage: dict[str, Any] | None = None

    def to_payload(self) -> dict[str, Any]:
        """Serialize to the proposed frontend-facing observation shape."""
        validated = ObservationSchema(
            status=self.status,
            pollutant=self.pollutant,
            value=self.value,
            unit=self.unit,
            observed_at=self.observed_at,
            source=self.source,
            provider=self.provider,
            station={
                "id": self.station_id,
                "name": self.station_name,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "sensor_id": self.sensor_id,
            },
            attribution=list(self.attribution),
            coverage=self.coverage,
        )
        return validated.model_dump(mode="json")


@dataclass
class IngestionReport:
    observations: list[Observation] = field(default_factory=list)
    rejected_records: int = 0
    duplicate_records: int = 0
    locations_seen: int = 0
    sensors_seen: int = 0
    rejected_by_reason: dict[str, int] = field(default_factory=dict)

    def reject(self, reason: str) -> None:
        self.rejected_records += 1
        self.rejected_by_reason[reason] = self.rejected_by_reason.get(reason, 0) + 1


def _request_json(
    path: str,
    *,
    api_key: str,
    base_url: str = OPENAQ_API_ROOT,
    params: dict[str, str | int] | None = None,
    timeout_seconds: float = 10,
) -> dict[str, Any]:
    if not api_key.strip():
        raise OpenAQError("OPENAQ_API_KEY is required for OpenAQ API access.")
    api_key = api_key.strip()

    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    if params:
        url = f"{url}?{urlencode(params)}"
    request = Request(url, headers={"X-API-Key": api_key, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code in {401, 403}:
            raise OpenAQAuthenticationError(
                f"OpenAQ rejected the API key ({exc.code}). Check OPENAQ_API_KEY and account access."
            ) from exc
        if exc.code == 429:
            raise OpenAQRateLimitError(
                "OpenAQ rate limit reached (429). Retry after the provider's reset window.",
                retry_after=exc.headers.get("Retry-After") if exc.headers else None,
            ) from exc
        raise OpenAQError(f"OpenAQ returned HTTP {exc.code}.") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise OpenAQError(f"Could not retrieve valid JSON from OpenAQ: {exc}.") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise OpenAQError("OpenAQ response did not contain a results list.")
    return payload


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if not math.isfinite(number) or number < 0:
        return None
    return number


def _coordinates(payload: Any) -> tuple[float, float] | None:
    if not isinstance(payload, dict):
        return None
    latitude_raw = payload.get("latitude")
    longitude_raw = payload.get("longitude")
    if (
        isinstance(latitude_raw, bool)
        or not isinstance(latitude_raw, (int, float))
        or isinstance(longitude_raw, bool)
        or not isinstance(longitude_raw, (int, float))
    ):
        return None
    latitude = float(latitude_raw)
    longitude = float(longitude_raw)
    if (
        not math.isfinite(latitude)
        or not math.isfinite(longitude)
        or not -90 <= latitude <= 90
        or not -180 <= longitude <= 180
    ):
        return None
    return latitude, longitude


def _utc_datetime(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    raw = value.get("utc")
    if not isinstance(raw, str):
        return None
    try:
        timestamp = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if timestamp.tzinfo is None:
        return None
    normalized = timestamp.astimezone(timezone.utc)
    if normalized > datetime.now(timezone.utc) + FUTURE_TIMESTAMP_TOLERANCE:
        return None
    return normalized.isoformat().replace("+00:00", "Z")


def _attributions(location: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    result: list[dict[str, Any]] = []
    licenses = location.get("licenses")
    if not isinstance(licenses, list):
        return ()
    for license_info in licenses:
        if not isinstance(license_info, dict):
            continue
        attribution = license_info.get("attribution")
        if not isinstance(attribution, dict):
            attribution = {}
        result.append(
            {
                "name": license_info.get("name") if isinstance(license_info.get("name"), str) else None,
                "attribution_name": attribution.get("name") if isinstance(attribution.get("name"), str) else None,
                "attribution_url": attribution.get("url") if isinstance(attribution.get("url"), str) else None,
            }
        )
    return tuple(result)


def _normalize_sensor(
    location: dict[str, Any], sensor: dict[str, Any]
) -> tuple[Observation | None, str | None]:
    station_id = location.get("id")
    station_name = location.get("name")
    coordinates = _coordinates(location.get("coordinates"))
    latest = sensor.get("latest")
    parameter = sensor.get("parameter")
    sensor_id = sensor.get("id")
    if (
        isinstance(station_id, bool)
        or not isinstance(station_id, (int, str))
        or not isinstance(station_name, str)
        or not station_name.strip()
        or not isinstance(sensor_id, (int, str))
        or isinstance(sensor_id, bool)
        or not isinstance(latest, dict)
        or not isinstance(parameter, dict)
    ):
        return None, "missing_station_or_sensor_metadata"
    if coordinates is None:
        return None, "invalid_or_missing_coordinates"

    value = _number(latest.get("value"))
    observed_at = _utc_datetime(latest.get("datetime"))
    pollutant = parameter.get("displayName") or parameter.get("name")
    unit = parameter.get("units")
    if value is None:
        return None, "invalid_value"
    if observed_at is None:
        return None, "invalid_or_future_timestamp"
    if not isinstance(pollutant, str) or not pollutant.strip() or not isinstance(unit, str) or not unit.strip():
        return None, "missing_pollutant_or_unit"

    provider = location.get("provider")
    provider_name = provider.get("name") if isinstance(provider, dict) else None
    latitude, longitude = coordinates
    return Observation(
        status="measured",
        pollutant=pollutant.strip(),
        value=value,
        unit=unit.strip(),
        observed_at=observed_at,
        source="OpenAQ",
        provider=provider_name if isinstance(provider_name, str) else None,
        station_id=str(station_id),
        station_name=station_name.strip(),
        latitude=latitude,
        longitude=longitude,
        sensor_id=str(sensor_id),
        attribution=_attributions(location),
        coverage=(sensor.get("coverage") if isinstance(sensor.get("coverage"), dict) else None),
    ), None


def fetch_delhi_latest(
    api_key: str,
    *,
    base_url: str = OPENAQ_API_ROOT,
    max_location_pages: int = 5,
    max_locations: int = 20,
    timeout_seconds: float = 10,
) -> IngestionReport:
    """Fetch and normalize latest data for up to five pages of Delhi stations.

    The bounded request avoids unbounded polling. This is a one-shot fetch,
    not a scheduler or persistent store. Source attribution and units are kept
    per record; freshness thresholds remain a project decision.
    """
    if max_location_pages < 1 or max_location_pages > 20:
        raise ValueError("max_location_pages must be between 1 and 20.")
    if max_locations < 1 or max_locations > 20:
        raise ValueError("max_locations must be between 1 and 20.")

    report = IngestionReport()
    seen: set[tuple[str, str, str]] = set()
    for page in range(1, max_location_pages + 1):
        page_data = _request_json(
            "locations",
            api_key=api_key,
            base_url=base_url,
            params={
                "coordinates": f"{DELHI_CENTER_LATITUDE},{DELHI_CENTER_LONGITUDE}",
                "radius": DELHI_SEARCH_RADIUS_METERS,
                "iso": "IN",
                "limit": 100,
                "page": page,
            },
            timeout_seconds=timeout_seconds,
        )
        locations = page_data["results"]
        if not locations:
            break

        for location in locations:
            if not isinstance(location, dict):
                report.reject("invalid_location_record")
                continue
            if location.get("isMonitor") is not True:
                continue
            location_id = location.get("id")
            report.locations_seen += 1
            if isinstance(location_id, bool) or not isinstance(location_id, (int, str)):
                report.reject("missing_location_id")
                continue

            sensors_data = _request_json(
                f"locations/{location_id}/sensors",
                api_key=api_key,
                base_url=base_url,
                params={"limit": 100, "page": 1},
                timeout_seconds=timeout_seconds,
            )
            for sensor in sensors_data["results"]:
                report.sensors_seen += 1
                if not isinstance(sensor, dict):
                    report.reject("invalid_sensor_record")
                    continue
                observation, rejection_reason = _normalize_sensor(location, sensor)
                if observation is None:
                    report.reject(rejection_reason or "invalid_observation")
                    continue
                key = (observation.station_id, observation.sensor_id, observation.observed_at)
                if key in seen:
                    report.duplicate_records += 1
                    continue
                seen.add(key)
                report.observations.append(observation)

            if report.locations_seen >= max_locations:
                return report

        meta = page_data.get("meta")
        found = meta.get("found") if isinstance(meta, dict) else None
        if not isinstance(found, int) or page * 100 >= found:
            break

    return report
