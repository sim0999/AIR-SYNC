# AirSync Backend — Branch Checklist and Starter Prompt

This document is the handoff for the person working on the `backend` branch on a separate machine. Work through one phase at a time, complete its exit check, and update this file as work is reviewed. The backend workspace has not been inspected in this audit, so its current implementation status must be confirmed by the backend developer.

## Current status

- **Branch:** `backend`
- **Workspace status:** To be checked on the backend developer's machine.
- **Current phase:** Phase 1 — Backend foundation
- **Phase 1 status:** Not assessed; confirm repository contents before marking anything complete.

## Phase 1 — Backend foundation and service contract

**Status:** Not assessed

- [ ] Inspect the backend branch and preserve existing work.
- [ ] Confirm Python/FastAPI version and dependency management approach.
- [ ] Create or confirm the FastAPI application entry point and local run instructions.
- [ ] Add a health endpoint, proposed as `GET /api/health` (coordinate the final path).
- [ ] Define and document an initial response contract for observation/prediction data with the frontend developer.
- [ ] Add configuration through environment variables where needed; do not commit secrets.
- [ ] Confirm CORS and same-origin expectations for local development and eventual deployment.

**Exit check:** The service starts locally, health response works, and the frontend developer has an agreed API contract to build against.

## Phase 2 — Data sources and ingestion

**Status:** Not started

- [ ] Confirm permitted and practical sources for Delhi air-quality observations (for example CPCB/DPCC or OpenAQ, subject to availability and terms).
- [ ] Record source, station ID, coordinates, pollutant, unit, and observation timestamp for each reading.
- [ ] Document refresh cadence, source limitations, and missing-data behavior.
- [ ] Handle time zones and units consistently.
- [ ] Add quality checks for duplicates, invalid coordinates, missing fields, outliers, and stale readings.
- [ ] Keep fixture/sample data clearly separated and labelled from live observations.

**Exit check:** Ingested records are traceable to a source and timestamp, and data quality/freshness behavior is documented.

## Phase 3 — Read/query API

**Status:** Not started; depends on Phase 1 contract and Phase 2 data availability.

- [ ] Implement the agreed observation/station endpoint(s).
- [ ] Validate query parameters and return clear client errors for invalid input.
- [ ] Return consistent units, timestamps, source identifiers, and data status.
- [ ] Define empty-result and upstream-failure behavior.
- [ ] Add the agreed `/api/predict` route only when its semantics and response fields are defined.
- [ ] Keep API docs/examples aligned with actual response models.

**Exit check:** The frontend can consume the service using the documented contract for success, empty, and failure cases.

## Phase 4 — Spatial baseline and evaluation

**Status:** Not started; requires sufficient trusted observations.

- [ ] Establish a transparent baseline such as inverse-distance weighting only if source coverage supports it.
- [ ] Record model inputs, units, assumptions, and support/coverage limitations.
- [ ] Validate using held-out locations, spatial block validation, or leave-one-station-out testing.
- [ ] Report suitable metrics such as MAE, RMSE, and bias with evaluation context.
- [ ] Do not invent accuracy, confidence, or safety claims.
- [ ] Return an explicit measured-versus-estimated indicator and coverage/status with every result.

**Exit check:** Any estimate exposed by the API has a documented method and evaluation; otherwise the API clearly returns unavailable/demo status.

## Phase 5 — Frontend integration and deployment readiness

**Status:** Not started

- [ ] Coordinate route names, schemas, units, timestamps, and CORS behavior with the frontend developer.
- [ ] Verify local frontend-to-backend integration.
- [ ] Confirm one combined deployment architecture with the frontend developer.
- [ ] Configure production routing/runtime for the actual app structure.
- [ ] Review hosting limits against model size and inference time.
- [ ] Verify deployed health and data routes and document required environment settings.

**Exit check:** Backend and frontend work together on the agreed deployment structure, with data provenance intact.

## Phase log

| Phase | Status | Notes |
|---|---|---|
| 1. Backend foundation and service contract | Not assessed | Confirm backend branch contents first |
| 2. Data sources and ingestion | Not started | |
| 3. Read/query API | Not started | Depends on contract and data |
| 4. Spatial baseline and evaluation | Not started | Depends on trusted observations |
| 5. Frontend integration and deployment readiness | Not started | Coordinate with frontend developer |

## Branch coordination rules

- Do backend work and commits on `backend`; do not commit frontend implementation on this branch.
- Keep the API contract documented and share changes with the frontend developer before changing field names or routes.
- Include units, source, timestamp, and measured/estimated/demo status in responses where applicable.
- Do not fabricate air-quality readings or report model performance before validation.
- Agree final merged layout and deployment routing together; a branch existing remotely does not mean its work is integrated into the deployable app.

## Shared API agreement (fill in together before Phase 3)

Do not treat these proposed route names or data definitions as final until both developers agree. Record the final contract here and in the frontend checklist.

| Decision | Agreed value |
|---|---|
| Health route and response | Pending |
| Observation route and response | Pending |
| Prediction route and response | Pending |
| AQI scale/category definition | Pending |
| Pollutant names and units | Pending |
| Timestamp format and timezone | Pending |
| Status values (measured / estimated / demo / unavailable) | Pending |
| Source and station fields | Pending |
| Empty result and error response | Pending |
| Local and deployed origin/routing | Pending |

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
