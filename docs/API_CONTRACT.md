# AirSync API Contract

**Frontend status:** Accepted for integration on 2026-11-01.  
**Backend status:** Confirmation from the backend developer is still required before this is considered jointly final.

This contract records the API proposal shared by the backend developer and the frontend's acceptance. It describes raw observations and prediction availability; it does not define or calculate AQI.

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

An invalid `max_locations` currently returns HTTP 422 with a structured error. The exact error JSON schema has not been provided in the shared proposal; the frontend uses a string `message` when present and otherwise displays a generic HTTP error.

## `GET /api/predict?latitude=…&longitude=…&pollutant=…`

Until a model has passed the documented validation review, return `status: "unavailable"`, `prediction: null`, and a message explaining why no estimate is provided. Do not label an unavailable result as measured.

If a validated model is connected later, return `status: "estimated"` and include the numeric `prediction`, its `unit`, and available `method`/`coverage` details. The frontend withholds an estimate if the unit is missing.

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
- Backend developer: please confirm this document or record requested changes before treating the contract as jointly final.
