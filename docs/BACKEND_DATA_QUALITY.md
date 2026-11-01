# AirSync backend data quality and freshness

**Scope:** Draft rules for the opt-in OpenAQ v3 adapter. No live records have been ingested in this workspace because no API key is configured. These rules do not imply that the source or API contract has been approved by the frontend developer.

## Alternative official source reviewed

India's OGD portal lists CPCB's [Real time Air Quality Index dataset](https://www.data.gov.in/resource/real-time-air-quality-index-various-locations), described as hourly station data collected from field instruments. The portal also states that registered users can generate API keys to access dataset API URLs, and that dataset content is licensed under the Government Open Data License - India ([portal help](https://www.data.gov.in/help)). This is a credible candidate for a future CPCB/OGD adapter, but no key or approved API URL/schema is available in this workspace. Its national AQI dataset also needs a schema and pollutant-level suitability review before it can replace OpenAQ for this project. No scraping or unapproved endpoint use is included.

## Record acceptance

The adapter accepts only a monitor location with a station ID/name, valid WGS 84 coordinates, a sensor ID, pollutant name, unit, finite nonnegative value, and timezone-aware UTC observation time. It rejects timestamps more than five minutes ahead of the ingestion clock to tolerate small source clock skew without accepting clearly future-dated readings.

Accepted timestamps are normalized to UTC. Source units are preserved as provided; no conversion or AQI calculation is performed. Each normalized record retains the OpenAQ source, underlying provider where available, station and sensor identifiers, source coverage metadata, and license/attribution metadata returned with the location.

## Duplicates and rejected records

The one-shot fetch de-duplicates on `(station_id, sensor_id, observed_at)`. The CLI reports both the rejected total and rejection counts by reason, including malformed location/sensor records, missing identifiers or metadata, invalid coordinates, invalid values, missing pollutant/unit, and invalid or future timestamps.

## Outliers and flags

The adapter rejects negative and non-finite values. It does not apply a statistical outlier threshold: no project-approved pollutant bounds, source-specific correction rules, or validation data are available. It does not convert unusual values into confidence or safety claims. Any source flags not included in the OpenAQ sensor response are not inferred.

## Spatial estimate safeguards

The initial baseline is inverse-distance weighting (IDW), using Haversine distance on WGS 84 coordinates and weights `1 / distance^power` (default power 2, bounded to `(0, 8]` to avoid unstable numerical inputs). Inputs must be measured records for one pollutant and one unit. The helper keeps only the newest eligible record per station and requires callers to supply the maximum reading age, maximum timestamp spread, and support radius; it defaults to at least three distinct stations. The target coordinates must not coincide with an observed station.

The helper is not wired to an API route. It returns no estimate when fewer than the required number of distinct measured stations support the query, units differ, records are stale/asynchronous, or the target coincides with a measured station. It reports the supporting station IDs, count, distances, radius, and timestamp span, not a confidence value. It does not convert pollutant values to AQI. `python -m api.modeling <snapshot> ...` runs leave-one-station-out evaluation separately for each pollutant/unit pair and reports MAE, RMSE, bias, sample count, and skipped predictions. The evaluator itself filters out non-measured records so demo or estimated values cannot enter validation even if a caller passes a mixed collection. It does not create performance claims without observations and actual predictions.

## Freshness and missing data

The adapter retains the source observation timestamp and coverage metadata. It does not label readings as fresh or stale because the project has not selected a freshness threshold or refresh cadence. An empty result is returned with `status: "unavailable"`; missing required record fields are counted as rejected. Upstream HTTP/authentication/rate-limit failures stop the fetch with an error rather than returning fabricated or cached measurements.

## Operational limits

The CLI is a bounded one-shot fetch (up to 20 monitor locations and five location pages), not a scheduler or shared persistence service. It can print a JSON snapshot to stdout or write to an explicit local path; generated `data/` snapshots are ignored by Git. `OPENAQ_API_KEY` must be set in the local environment. Before production use, confirm the upstream provider's license/attribution for each returned location and choose an approved refresh cadence and shared persistence strategy.
