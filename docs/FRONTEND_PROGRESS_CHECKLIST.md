# AirSync Frontend — Branch Checklist

This document is for the person working on the `frontend` branch in the frontend workspace. Work through one phase at a time: finish its checklist, review it, and update the status before starting the next phase.

## Current status

- **Branch:** `frontend`
- **Workspace reviewed:** `C:\Users\ry105\OneDrive\Desktop\New folder\AIR-SYNC`
- **Current phase:** Phase 5 — Backend API integration (blocked on backend contract)
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

**Status:** Blocked — checked `origin/backend`; it currently contains only `README.md` and project documentation, with no FastAPI implementation or API contract.

- [ ] Agree the JSON response shape and route names with the backend developer before wiring the UI.
- [ ] Add a dedicated API module and use same-origin/relative routes such as `/api/health` and `/api/predict` if agreed.
- [ ] Handle loading, success, empty, and error responses.
- [ ] Map response fields to the dashboard without inventing missing measurements.
- [ ] Document any backend contract mismatch for coordination.

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
| 5. Backend API integration | Blocked | Backend branch currently has no API implementation/contract; agree routes and JSON fields with backend developer |
| 6. Accessibility and integration readiness | Not started | |

## Branch coordination rules

- Do frontend work and commits on `frontend`; do not commit backend implementation on this branch.
- Keep UI structure and styling independent of backend internals.
- Agree API paths, field names, units, timestamps, and status labels with the backend developer before integration.
- Use demo fixtures only when clearly labelled; never present them as real air-quality observations.
- Merge branches only when both sides are ready and the integration structure has been agreed.

## Shared API agreement (fill in together before Phase 5)

These are decisions for both developers; the frontend should not guess them and the backend should not silently change them.

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

Record the final agreement here and in the backend's API docs before wiring frontend API calls.

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
