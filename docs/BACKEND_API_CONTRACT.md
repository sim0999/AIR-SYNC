# AirSync backend API contract proposal

**Status: Proposal in use by the frontend, with details still pending agreement.** The frontend developer reports that the UI is wired to these proposed routes. The backend response shapes are implemented, but cross-computer browser integration and agreement on AQI, units, and error/empty handling remain to be reviewed. No data source or prediction method is claimed to be ready.

## Implemented routes

### `GET /api/health`

Returns HTTP 200 when the API process is responding:

```json
{
  "status": "ok",
  "service": "airsync-api"
}
```

This is a process health check, not a data or model readiness check.

### `GET /api/predict`

Requires `latitude`, `longitude`, and `pollutant` query parameters. It currently returns HTTP 200 with `status: "unavailable"`, `prediction: null`, and a message that no validated model is available. Invalid coordinates or missing/invalid query values return HTTP 422 in the shared error envelope. The route never substitutes demo or unvalidated IDW output.

Example unavailable response:

```json
{
  "status": "unavailable",
  "latitude": 28.6139,
  "longitude": 77.209,
  "pollutant": "PM2.5",
  "prediction": null,
  "method": null,
  "coverage": null,
  "message": "No validated spatial model is available; no estimate is provided."
}
```

### `GET /api/observations`

With `AIRSYNC_ENABLE_OPENAQ` unset or false, returns HTTP 200 with an explicit empty state:

```json
{
  "status": "unavailable",
  "source": null,
  "observations": [],
  "message": "Live observation source is disabled."
}
```

With the feature enabled and an authorized `OPENAQ_API_KEY`, it requests latest sensor metadata for up to `max_locations` (default 3, maximum 5) Delhi monitoring locations and returns normalized measured records. The route performs at most one location page lookup and uses a three-second timeout per provider call. It returns 503 if the key is missing/invalid or the provider rate-limits the request, 502 for other upstream failures, and 422 for an invalid location limit. A provider `Retry-After` header is forwarded when available. It does not cache or poll automatically. The response message states that this bounded station sample is not complete Delhi coverage. The response shape is implemented as a proposal and still needs frontend agreement before it is treated as the shared contract.

## Proposed observation record

```json
{
  "status": "measured",
  "pollutant": "PM2.5",
  "value": 0,
  "unit": "<source-defined unit>",
  "observed_at": "<ISO 8601 timestamp with offset or Z>",
  "source": "<provider identifier>",
  "provider": "<underlying data provider or null>",
  "station": {
    "id": "<provider station identifier>",
    "name": "<station name or null>",
    "latitude": 0,
    "longitude": 0,
    "sensor_id": "<provider sensor identifier>"
  },
  "attribution": [
    {
      "name": "<license name>",
      "attribution_name": "<required credit or null>",
      "attribution_url": "<credit URL or null>"
    }
  ],
  "coverage": "<source-provided coverage object or null>"
}
```

The zero and angle-bracket values above are schema examples only, not readings. The proposed initial source adapter is OpenAQ v3, which requires a registered API key and exposes underlying provider and license details. The final pollutant vocabulary, units, nullability, AQI mapping, timestamp rules, and station fields must follow source terms and frontend agreement.

## Proposed query and response behavior

- `/api/observations` returns `status: "unavailable"` when disabled or when no valid readings are found. `max_locations` is bounded from 1 to 5 to constrain provider calls.
- Invalid query parameters return HTTP 422 with a consistent `error.code`, `error.message`, and `error.field_errors` envelope.
- Missing credentials and provider 401/403 authentication rejections return HTTP 503; provider rate limits return HTTP 503 and forward `Retry-After` when available.
- Other upstream source failures return HTTP 502. Errors never return cached or fabricated values presented as current.
- Unexpected server errors return HTTP 500 with the same envelope and a generic message; implementation details stay in server logs.
- The draft one-shot CLI prints an empty `observations` list with `status: "unavailable"` when no valid records are returned, and exits with an error message on upstream failure.
- Every observation should carry its source, station identity/location, pollutant, unit, timestamp, and `measured` status.
- `/api/predict` is defined as a contract endpoint but always returns unavailable until a method has sufficient trusted data and validation. The IDW helper is not wired into the route.
- Response models reject inconsistent envelopes: unavailable collections cannot contain readings; measured collections require at least one measured record and a source; estimated predictions require a value and method; unavailable predictions cannot include a value.

Example validation error:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "One or more request parameters are invalid.",
    "field_errors": [
      { "field": "query.max_locations", "message": "Input should be less than or equal to 5" }
    ]
  }
}
```

## Decisions still required

| Decision | Current state |
|---|---|
| Observation route and query parameters | Backend v1 proposal: `GET /api/observations?max_locations=3` (1–5); frontend agreement pending |
| Prediction route and semantics | Backend v1 proposal: `GET /api/predict?latitude=…&longitude=…&pollutant=…`; returns unavailable until a validated model exists; frontend agreement pending |
| AQI scale/category definition | Pending |
| Pollutant names and units | Source-dependent; pending |
| Timestamp format and timezone | Backend v1 proposal: timezone-aware UTC ISO 8601; frontend agreement pending |
| Data status values | Backend v1 proposal: `measured` or `unavailable`; `estimated` only after model validation |
| Empty result and error envelope | Backend proposal implemented; frontend agreement pending |
| Source and station fields | OpenAQ source/provider, station/sensor IDs, coordinates, units, coverage, and attribution |
| Browser origin/CORS and deployment routing | Same-origin by default; local exact origins configurable via `AIRSYNC_CORS_ORIGINS`; combined deployment not configured |

## Source references

- [OpenAQ v3 quick start](https://docs.openaq.org/using-the-api/quick-start) documents the API key header, New Delhi station example, coordinates, sensor IDs, units, UTC/local timestamps, and license attribution.
- [OpenAQ API terms](https://docs.openaq.org/about/terms) require registered programmatic use, OpenAQ attribution, and compliance with each underlying provider's terms.
- [OpenAQ locations endpoint](https://docs.openaq.org/api/operations/locations_get_v3_locations_get) documents coordinate/radius search, ISO country filter, and pagination.
- [OpenAQ sensors-by-location endpoint](https://docs.openaq.org/api/operations/sensors_get_v3_locations__locations_id__sensors_get) documents sensor parameters, units, latest value, timestamps, and coordinates.
- [OpenAQ rate limits](https://docs.openaq.org/using-the-api/rate-limits) document 60 requests/minute and 2,000 requests/hour for general use. The one-shot adapter caps itself at 20 station sensor lookups plus a maximum of five location pages and does not poll continuously.

The adapter is implemented as an opt-in API route and one-shot CLI (`python -m api.ingestion`). No upstream calls occur unless `AIRSYNC_ENABLE_OPENAQ=true`. Before enabling it for the product, configure an authorized `OPENAQ_API_KEY`, review each returned provider/license, and agree the public response contract with the frontend developer.
