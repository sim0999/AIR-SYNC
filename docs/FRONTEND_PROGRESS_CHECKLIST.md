# AirSync Frontend — Branch Checklist

This document is for the person working on the `frontend` branch in the frontend workspace. Work through one phase at a time: finish its checklist, review it, and update the status before starting the next phase.

## Current status

- **Branch:** `frontend`
- **Workspace reviewed:** `C:\Users\ry105\OneDrive\Desktop\New folder\AIR-SYNC`
- **Current phase:** Phase 5 — Backend API integration (backend reachable; connected UI empty-state review pending)
- **Phase 1 status:** Complete
- **Audit finding:** The workspace initially had no frontend implementation. Phase 1 now has a root page with separate CSS and JavaScript files.

## Phase 1 — UI foundation

**Status:** Complete

- [x] Create the semantic page structure and AirSync branding/navigation.
- [x] Add the “Breathe Better. Know Your Air.” hero and concise project description.
- [x] Add location search, Search, and Use My Location controls.
- [x] Add an AQI summary and map container.
- [x] Explain measured observations versus modelled estimates; include the footer.
- [x] Keep HTML, CSS, and JavaScript separate; use accessible labels and unique IDs.
- [x] Label all sample values as demo data; do not imply measurements are live.
- [x] Preview and review this phase before moving on.

**Exit check:** All page sections exist, assets/scripts load, and demo content is clearly identified.

## Phase 2 — Interactive map

**Status:** Complete

- [x] Integrate Leaflet with OpenStreetMap and centre the map on Delhi.
- [x] Add pan/zoom controls and a readable legend.
- [x] Add clearly labelled demo station markers and an estimated-area treatment.
- [x] Visually distinguish observed, estimated, and demo information.
- [x] Keep map behavior in a dedicated module.
- [x] Review map behavior before moving on.

**Exit check:** The map works and the legend makes each data type clear.

## Phase 3 — AQI dashboard

**Status:** Complete

- [x] Show AQI/category, PM2.5, and PM10.
- [x] Show the default Delhi view and approximate map-centre coordinates.
- [x] Show source, timestamp, and status/coverage when available; identify unavailable values honestly.
- [x] Label demo values and avoid invented accuracy/confidence claims.

**Exit check:** Every displayed value has an honest status and provenance or is explicitly demo content.

## Phase 4 — Search and device location

**Status:** Complete — OpenStreetMap Nominatim selected by the project owner.

- [x] Integrate OpenStreetMap Nominatim for user-submitted searches; do not add autocomplete.
- [x] Add browser geolocation to Use My Location; request permission only after the user clicks.
- [x] Show geolocation permission, loading, success, timeout, and error feedback, plus geocoder loading, results, no-result, and service-error states.
- [x] Keep selected place/device location and map/dashboard context in sync; hide Delhi-only demo overlays when showing another location.
- [x] Keep location behavior in dedicated `location.js` and `map.js` modules.
- [x] Disclose that submitted place searches go to Nominatim; warn users not to enter private or confidential details.
- [x] Limit requests to one per 1.1 seconds per page and cache repeated queries in memory.

**Deployment note:** Per-page throttling does not enforce a limit across all visitors. Before public deployment or increased traffic, route searches through a backend proxy with shared caching/rate limiting or switch to a provider suited to the app's usage. Nominatim autocomplete is prohibited.

**Exit check:** Search and device location handle expected states without hardcoded secrets or fabricated results.

## Phase 5 — Backend API integration

**Status:** In progress — frontend and backend contract v1 is jointly recorded and the route/CORS checks pass. The connected UI empty-state review and live readings remain open.

- [x] Record the backend v1 route names, response shape, status semantics, and source units below.
- [x] Add a dedicated API module for `/api/health`, `/api/observations?max_locations=3`, and `/api/predict`.
- [x] Handle loading, unavailable, empty, malformed, timeout, and network-error responses.
- [x] Map measured observations to station markers and dashboard fields without inventing measurements.
- [x] Keep AQI uncalculated because the project has not selected a scale; only display estimates explicitly marked `estimated` and carrying a unit.
- [x] Confirm backend health and observations responses, frontend preview response, and CORS preflight from this machine.
- [ ] Review the connected UI in a browser, including its unavailable-observations state.
- [x] Record frontend acceptance and AQI deferral in [API_CONTRACT.md](API_CONTRACT.md).
- [x] Obtain backend developer confirmation; see the signed-off backend semantics in [API_CONTRACT.md](API_CONTRACT.md).

**Exit check:** Frontend uses the agreed contract and preserves source, timestamp, units, and measured/estimated status.

## Phase 6 — Accessibility, responsive review, and integration readiness

**Status:** Not started

- [ ] Review mobile and desktop layouts.
- [ ] Review semantic HTML, keyboard operation, labels, and contrast.
- [ ] Review loading/error/empty states and measured/estimated/demo wording.
- [ ] Verify paths, IDs, and browser console behavior.
- [ ] Record integration assumptions and unresolved gaps for the backend developer.

**Exit check:** Core frontend flows are understandable and ready to integrate with the backend branch.

## Phase log

| Phase | Status | Notes |
|---|---|---|
| 1. UI foundation | Complete | Browser preview reviewed at mobile width; demo labels and placeholder control feedback confirmed |
| 2. Interactive map | Complete | OSM tiles loaded; zoom controls and a demo marker popup reviewed in browser; attribution visible |
| 3. AQI dashboard | Complete | Browser review confirmed demo values, approximate map-centre location, demo-fixture source, unavailable timestamp, and unavailable coverage |
| 4. Search and device location | Complete | Nominatim place search and map selection reviewed with a Delhi query; device permission path remains user-triggered and was not invoked during review. |
| 5. Backend API integration | In progress | `http://192.168.160.226:8000/api/health` returned 200 (`status: ok`); `/api/observations?max_locations=3` returned 200 with unavailable status and an empty list; CORS preflight for `http://localhost:5500` returned 200. Frontend page returned 200. Backend v1 contract is confirmed; live readings and connected UI empty-state review remain pending. |
| 6. Accessibility and integration readiness | Not started | |

## Branch coordination rules

- Do frontend work and commits on `frontend`; do not commit backend implementation on this branch.
- Keep UI structure and styling independent of backend internals.
- Follow the jointly recorded API paths, field names, units, timestamps, and status labels; coordinate any later contract revisions.
- Use demo fixtures only when clearly labelled; never present them as real air-quality observations.
- Merge branches only when both sides are ready and the integration structure has been agreed.

## Joint frontend/backend API acceptance

The frontend accepts and the backend confirms the v1 routes and fields in this table. Full details are in [API Contract](API_CONTRACT.md).

| Decision | Agreed value |
|---|---|
| Health route and response | Frontend accepts `GET /api/health`; verified response is `{"status":"ok","service":"airsync-api"}` |
| Observation route and response | Frontend accepts `GET /api/observations?max_locations=3`; limit 1–5; collection has `status`, `source`, `observations`, `message` |
| Prediction route and response | Frontend accepts `GET /api/predict?latitude=…&longitude=…&pollutant=…`; remains unavailable until a model passes validation; estimated values require a unit |
| AQI scale/category definition | No scale chosen; accepted scope is no AQI calculation or category until a separate team decision |
| Pollutant names and units | Preserve provider-defined names and units without conversion |
| Timestamp format and timezone | UTC ISO 8601 |
| Status values (measured / estimated / demo / unavailable) | Source readings use `measured`; predictions use `estimated` only after validation; unavailable results use `unavailable`; demo overlays are frontend-only |
| Source and station fields | Observation: `status`, `pollutant`, `value`, `unit`, `observed_at`, `source`, `provider`, `station`, `attribution`, `coverage`; station: `id`, `name`, `latitude`, `longitude`, `sensor_id` |
| Empty result and error response | Unavailable observations return status, null source, empty list, and message; errors use `{error:{code,message,field_errors?}}`; invalid limits return structured HTTP 422 |
| Local and deployed origin/routing | Backend at `http://192.168.160.226:8000`; configured as `AIRSYNC_CONFIG.apiBaseUrl`; CORS preflight from `http://localhost:5500` verified successfully |

Frontend acceptance and backend confirmation are recorded in [API_CONTRACT.md](API_CONTRACT.md). The connected UI empty-state review is the remaining Phase 5 frontend check.

See [AirSync Project Plan](AirSync_Project_Plan.md) for product scope and data-integrity principles, and [Backend Progress Checklist](BACKEND_PROGRESS_CHECKLIST.md) for the other branch's work plan and starter prompt.

## Frontend autonomous-work prompt

Copy this prompt into Codex in the frontend workspace when you want it to carry out the frontend plan:

> Work on AirSync's `frontend` branch in this workspace. Implement the frontend plan in `docs/FRONTEND_PROGRESS_CHECKLIST.md`, using `docs/AirSync_Project_Plan.md` for product scope and data integrity rules. First inspect the repository and preserve existing work. Do not modify backend implementation or switch branches.
>
> Work through the frontend phases in order, one phase at a time. Finish the current phase's checklist and exit check before starting the next phase; update the checklist as you go. Continue autonomously through phases that are unblocked. If a decision, credential, data source, or backend contract is required and cannot be inferred safely, record the blocker and continue with independent frontend work without inventing a value or contract.
>
> Build the UI with separate HTML, CSS, and JavaScript files. Keep the app understandable and accessible. Use demo fixtures only when clearly labelled as demo. Never present sample values as live observations, claim an estimate is accurate without validation, or imply that a place is safe.
>
> For the map, use Leaflet/OpenStreetMap as specified in the project plan. For location search, do not select a paid/provider-specific geocoder or embed a key without an agreed provider and configuration. Browser geolocation should explain permission and failure states.
>
> Before API integration, coordinate with the backend developer and use only the agreed routes, response fields, units, timestamps, and measured/estimated status. Keep calls configurable and use relative same-origin paths where the agreed deployment supports them. Handle loading, empty, and error responses.
>
> After each phase, summarize the changes, what was reviewed, checklist status, and any blocker. Do not claim work is complete unless the phase exit check is met. Do not push, merge, or deploy unless explicitly asked.
