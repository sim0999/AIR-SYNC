# AirSync Backend — Branch Checklist and Starter Prompt

This document tracks implementation on the `backend` branch. Work through phases in order; when the project owner authorizes multi-phase work, advance independent pieces together and keep prerequisite-dependent items open. Update each status only with implementation evidence.

## Current status

- **Branch:** `backend`
- **Workspace status:** Inspected in the current checkout; backend foundation added.
- **Current phase:** Phase 1 — Backend foundation and service contract
- **Phase 1 status:** Backend v1 contract is finalized for integration; frontend reports route wiring. Cross-computer browser review remains pending.

## Phase 1 — Backend foundation and service contract

**Status:** In progress

- [x] Inspect the backend branch and preserve existing work.
- [x] Select Python dependency management with `requirements.txt`; Python 3.12 is available in this workspace.
- [x] Create the FastAPI application entry point and local run instructions.
- [x] Add and locally verify the proposed `GET /api/health` endpoint (HTTP 200).
- [x] Freeze and document backend v1 health, observation, prediction, empty/error, status, unit, timestamp, and CORS behavior for the frontend routes it reports wiring.
- [ ] Verify frontend field mapping and the end-to-end browser connection in the separate frontend workspace.
- [x] Read the optional `OPENAQ_API_KEY` from the environment; no key is stored in the repository. Remaining provider settings are passed as explicit adapter arguments.
- [x] Default to same-origin; configure optional exact local CORS origins with `AIRSYNC_CORS_ORIGINS`. Final deployment agreement remains pending because frontend files are not present.

**Exit check:** The service starts locally, health response works, and the frontend developer has an agreed API contract to build against.

## Phase 2 — Data sources and ingestion

**Status:** Adapter and one-shot CLI are implemented but gated; do not enable OpenAQ until source authorization and provider/license review are complete.

- [ ] Confirm OpenAQ as the project source, provide an authorized API key, and review the returned underlying provider/license terms.
- [x] Preserve source, provider, station/sensor IDs, coordinates, pollutant, units, timestamp, and available attribution in normalized records.
- [x] Document the adapter's one-shot behavior, local snapshot output, empty/failure behavior, and source limitations; refresh cadence remains pending.
- [x] Record current validation, duplicate, outlier, and freshness handling in [Backend Data Quality](BACKEND_DATA_QUALITY.md).
- [x] Normalize timestamps to UTC while preserving the source unit without conversion.
- [ ] Complete quality policy for outliers and stale readings; adapter records rejection counts by reason, rejects malformed, negative, non-finite, coordinate-invalid, missing-required-field, and timestamps more than five minutes in the future, and deduplicates by station/sensor/timestamp. Stale readings are retained with timestamps; a freshness threshold remains pending.
- [ ] Keep fixture/sample data clearly separated and labelled from live observations.

**Exit check:** Ingested records are traceable to a source and timestamp, and data quality/freshness behavior is documented.

## Phase 3 — Read/query API

**Status:** Implemented behind an explicit source opt-in; backend v1 contract is documented, while frontend browser review and live-source credentials remain pending.

- [ ] Implement the agreed observation/station endpoint(s).
- [x] Validate `max_locations` and return a structured 422 error for invalid input.
- [x] Return source units, UTC timestamps, source identifiers, and measured/unavailable status.
- [x] Define empty-result, missing-credential, rate-limit, upstream-failure, and unexpected-error behavior.
- [x] Define and implement the proposed `/api/predict` route as an explicit unavailable response until its model is validated and the frontend agrees to the contract.
- [x] Enforce response-state consistency in the schemas: measured collections must have measured records and a source; unavailable collections cannot contain records; prediction value/method must match estimated versus unavailable status.
- [x] Keep API docs/examples aligned with actual response models and error envelopes.

**Exit check:** The frontend can consume the service using the documented contract for success, empty, and failure cases.

## Phase 4 — Spatial baseline and evaluation

**Status:** Baseline and snapshot-based holdout evaluation workflow implemented but not run; requires sufficient trusted observations before any estimate can be exposed.

- [x] Implement a guarded inverse-distance-weighting helper; keep it unavailable until source coverage is sufficient.
- [x] Record model inputs, units, assumptions, and support/coverage limitations in `docs/BACKEND_DATA_QUALITY.md`.
- [x] Add a leave-one-station-out evaluation CLI; it requires an explicit saved snapshot and freshness/support settings.
- [ ] Run and review validation using held-out locations, spatial block validation, or leave-one-station-out testing.
- [ ] Report suitable metrics such as MAE, RMSE, and bias with evaluation context.
- [ ] Do not invent accuracy, confidence, or safety claims.
- [ ] Return an explicit measured-versus-estimated indicator and coverage/status with every result.

**Exit check:** Any estimate exposed by the API has a documented method and evaluation; otherwise the API clearly returns unavailable/demo status.

## Phase 5 — Frontend integration and deployment readiness

**Status:** Backend v1 contract documented and aligned to the routes the frontend developer reports wiring. AQI remains uncalculated. Cross-computer browser verification and confirmation of the UI field mapping remain pending.

- [x] Define the backend v1 route, schema, unit, timestamp, status, empty/error, and CORS contract for the routes the frontend developer reports wiring.
- [ ] Verify frontend field mapping and CORS from the frontend browser/workspace.
- [ ] Verify local frontend-to-backend integration.
- [ ] Confirm one combined deployment architecture with the frontend developer.
- [x] Prepare Vercel Python runtime configuration for the backend entry point; final combined frontend routing remains pending.
- [ ] Review hosting limits against model size and inference time.
- [ ] Verify deployed health and data routes and document required environment settings.

**Exit check:** Backend and frontend work together on the agreed deployment structure, with data provenance intact.

## Phase log

| Phase | Status | Notes |
|---|---|---|
| 1. Backend foundation and service contract | Contract v1 defined; browser check pending | Added `api/index.py`, `requirements.txt`, local instructions, and the v1 contract. FastAPI returned HTTP 200 on the LAN address; the frontend developer reports wiring the routes. |
| 2. Data sources and ingestion | Prepared (source review pending) | OpenAQ v3 adapter and one-shot CLI added with bounded Delhi lookup, field validation, UTC normalization, duplicate rejection, coverage metadata, attribution retention, and rejection counts by reason. Quality/freshness behavior documented. Requires an authorized key and provider/license review; no scheduled ingestion or persistence. |
| 3. Read/query API | Implemented (source opt-in) | Added typed `/api/observations` and `/api/predict`, with schema checks preventing inconsistent measured/unavailable/estimated envelopes. Observations default unavailable; opt-in OpenAQ reads are bounded to five stations/one location page. Prediction always returns unavailable until a validated model is connected. Errors use structured 422, 500, 502, and 503 responses. Health, unavailable, and invalid-query responses verified; live fetch remains unverified because no key is configured. Backend v1 contract is documented; frontend browser review remains pending. |
| 4. Spatial baseline and evaluation | Prepared (unevaluated) | Added guarded IDW, a snapshot-based leave-one-station-out CLI, and MAE/RMSE/bias reporting by pollutant/unit. No trusted readings exist in the workspace, so no evaluation metrics are reported and no estimate route is exposed. |
| 5. Frontend integration and deployment readiness | Prepared (browser review pending) | Added `.python-version`, Vercel FastAPI deployment notes, and a 30-second function bound for the limited upstream call path. Frontend route wiring is reported by its developer but the files are in a separate workspace; LAN health, empty observations, 422 validation, and localhost:5500 CORS preflight were checked from this backend computer. No remote browser check or deployment was performed. |

## Branch coordination rules

- Do backend work and commits on `backend`; do not commit frontend implementation on this branch.
- Keep the API contract documented and share changes with the frontend developer before changing field names or routes.
- Include units, source, timestamp, and measured/estimated/demo status in responses where applicable.
- Do not fabricate air-quality readings or report model performance before validation.
- Agree final merged layout and deployment routing together; a branch existing remotely does not mean its work is integrated into the deployable app.

## Backend/frontend API contract v1

The backend v1 contract is frozen in [Backend API Contract](BACKEND_API_CONTRACT.md) for the routes the frontend developer reports wiring. AQI is omitted, and provider pollutant values/units pass through unchanged. The frontend browser review remains open because its source workspace is not available in this checkout.

| Decision | Backend v1 |
|---|---|
| Health route and response | `GET /api/health` → `{"status":"ok","service":"airsync-api"}` |
| Observation route and response | `GET /api/observations?max_locations=3` (1–5); status/source/observations/message envelope |
| Prediction route and response | `GET /api/predict` returns unavailable until model validation |
| AQI scale/category definition | Not returned or calculated until a scale is selected |
| Pollutant names and units | Provider names/units pass through unchanged |
| Timestamp format and timezone | Timezone-aware UTC ISO 8601 |
| Status values (measured / estimated / demo / unavailable) | Observation `measured`/`unavailable`; prediction unavailable until validated; no demo records served |
| Source and station fields | OpenAQ source/provider, station/sensor IDs, coordinates, coverage, and attribution |
| Empty result and error response | HTTP 200 unavailable empty list; errors `{error:{code,message,field_errors?}}`, status 422/502/503/500 |
| Local and deployed origin/routing | Same-origin default; local CORS uses `AIRSYNC_CORS_ORIGINS`; combined deployment pending |

## Backend starter prompt

Copy the prompt below into the backend project workspace after checking out the `backend` branch:

> You are working on the AirSync `backend` branch. Build the FastAPI backend for a hyperlocal air-quality mapping project initially focused on Delhi. The frontend is being developed separately on the `frontend` branch and must remain untouched by this backend task.
>
> First inspect the existing repository and preserve all existing work. Confirm this checklist is present in your workspace; if it is not, get it from the frontend developer or recreate it from the agreed plan before proceeding. Do not assume files, providers, data, or model results exist unless the repository confirms them. Work through the phases in `docs/BACKEND_PROGRESS_CHECKLIST.md` in order, completing and reviewing one phase before beginning the next. Update the checklist as you go and continue autonomously through phases that are unblocked.
>
> Establish or confirm the FastAPI app entry point, dependency/run instructions, a health endpoint, environment-based configuration, and an initial API response contract. Coordinate route names and JSON fields with the frontend developer before treating the contract as final. Proposed routes are `GET /api/health` and `GET /api/predict`; treat these as proposals until agreed. Continue through data ingestion, API implementation, spatial baseline/evaluation, and integration readiness only when each phase's prerequisites are met.
>
> Keep the backend organized and document how to run it locally. Use explicit request/response models and clear error handling. Never commit API keys or secrets. Do not change frontend files or claim the frontend/backend branches are integrated. Do not push, merge, or deploy unless explicitly asked.
>
> Air-quality integrity requirements:
> - Preserve source, station identifier, coordinates, pollutant, units, and timestamps for observations.
> - Clearly distinguish measured observations, modelled estimates, and demo/fixture data in API responses.
> - Do not fabricate real readings, confidence values, validation metrics, or claims that a location is safe.
> - Add ingestion and quality checks only after confirming data source availability, access terms, and schema.
> - Build spatial estimation only when sufficient trusted data exist; start with an explainable baseline and validate it using spatially appropriate held-out data before exposing accuracy claims.
>
> After each phase, summarize files changed, how to run or review the work, checklist status, and any decisions or blockers for the frontend developer. Leave a phase unchecked until it is implemented and its exit check is met. If an external decision or trustworthy data source is missing, do not fabricate one: document the blocker and continue only with independent, safe work.

See [AirSync Project Plan](AirSync_Project_Plan.md) for the overall product scope and data integrity principles, and [Frontend Progress Checklist](FRONTEND_PROGRESS_CHECKLIST.md) for the frontend branch plan.
