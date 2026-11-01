# AirSync API Contract

**Frontend status:** Accepted for integration on 2026-11-01.
**Backend status:** Confirmed for v1 on 2026-11-01. The connected UI empty-state review remains pending.

This contract records the frontend acceptance and backend confirmation. It describes raw observations and prediction availability; it does not define or calculate AQI.

## `GET /api/health`

Returns HTTP 200 when the service is responding. The running backend returned:

```json
{
  "status": "ok",
  "service": "airsync-api"
}
```

## `GET /api/observations?max_locations=3`

`max_locations` is an integer from 1 to 5. The collection response contains:

```json
{
  "status": "measured | unavailable",
  "source": "provider name or null",
  "observations": [],
  "message": "Human-readable status"
}
```

When observations are unavailable, return `status: "unavailable"` and an empty `observations` array. The currently running backend returned HTTP 200 with this unavailable form because its live source is disabled.

Each returned observation has these fields:

- `status`: `measured` for a reading supplied by the data source.
- `pollutant`, `value`, `unit`: retain the provider's pollutant label, numeric value, and unit without conversion.
- `observed_at`: UTC ISO 8601 timestamp.
- `source`, `provider`: provenance for the reading.
- `station`: object with `id`, `name`, `latitude`, `longitude`, and `sensor_id`.
- `attribution`, `coverage`: provider attribution and coverage information, or `null`/empty when unavailable.

Only readings with usable station coordinates can be placed on the map. The frontend displays a reading as measured only when its observation status is `measured`; demo overlays remain explicitly illustrative.

## Invalid requests and other errors

Invalid query parameters return HTTP 422 with this structured envelope. The frontend API client reads `error.message` and any optional `field_errors`:

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

Other errors use the same `error.code` and `error.message` envelope: 503 for credentials or rate limiting, 502 for other upstream failures, and 500 for unexpected errors. `Retry-After` is forwarded when the provider supplies it.

## `GET /api/predict?latitude=…&longitude=…&pollutant=…`

Until a model has passed the documented validation review, return `status: "unavailable"`, `prediction: null`, `unit: null`, and a message explaining why no estimate is provided. Do not label an unavailable result as measured.

If a validated model is connected later, return `status: "estimated"` and include the numeric `prediction`, its top-level `unit`, and `method`/`coverage` details. The frontend withholds an estimate if the unit is missing.

## AQI decision

No AQI scale or category mapping has been selected. Under this accepted contract, the backend does not calculate AQI and the frontend displays no AQI value or category. The team must agree on a named scale, averaging periods, pollutant inputs, and category thresholds before adding AQI fields or calculations.

## Development and deployment

- Development backend currently runs at `http://192.168.160.226:8000`.
- The frontend uses `AIRSYNC_CONFIG.apiBaseUrl` for the API origin.
- The backend has been verified to allow the frontend origin `http://localhost:5500` through CORS.
- A combined deployment may use same-origin `/api/...` routing by setting `apiBaseUrl` to an empty string and configuring the host/proxy accordingly.

## Acceptance record

- Frontend accepts the health, observations, and prediction routes and the fields/status rules above.
- Frontend accepts provider-defined pollutant labels and units without conversion.
- Frontend accepts that AQI remains explicitly uncalculated until the team selects and documents a scale.
- Backend confirms the v1 routes and semantics. The estimate field is a flat number with a sibling `unit`, matching `js/app.js`.
