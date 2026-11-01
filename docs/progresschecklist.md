# AirSync Project Progress Checklist

**Last reviewed:** 2026-11-01
**Working branch:** `frontend`
**Rule:** Complete and review one phase before starting the next. Update this checklist as work is completed; do not mark planned or documented work as implemented.

## Current project snapshot

- [x] Reviewed the repository contents, existing project plan, and Git state.
- [x] Recorded an implementation checklist organized into sequential phases.
- [x] Phase 1 — UI foundation (implemented and reviewed in browser).
- [x] Phase 2 — Interactive map (implemented and reviewed in browser).
- [x] Phase 3 — AQI dashboard (implemented and reviewed in browser).
- [x] Phase 4 — Search and device location (Nominatim search and geolocation support implemented; browser-reviewed).
- [ ] Phase 5 — Frontend API integration (frontend acceptance and backend v1 confirmation recorded; connected UI empty-state review pending).

At the initial audit, the workspace contained a zero-byte root `index.html`, a minimal `README.md`, and project documentation. Phases 1–4 were implemented and reviewed in a browser. Phase 5 wires the frontend to the jointly confirmed v1 contract in `docs/API_CONTRACT.md`: `/api/health`, `/api/observations`, and `/api/predict`, using `http://192.168.160.226:8000` as its configured API origin. From the frontend machine, health and observations each returned 200, the observations response was unavailable with an empty list, the CORS preflight for `http://localhost:5500` returned 200, and the local frontend page returned 200. The connected UI empty-state review remains open. AQI remains uncalculated until a scale is selected.

## Phase 1 — UI foundation

**Status:** Complete
**Goal:** Build the semantic, responsive page shell described in the project plan.

- [x] Add AirSync branding and navigation.
- [x] Add the hero heading, project introduction, location search, Search, and Use My Location controls.
- [x] Add initial AQI summary and map container, with any placeholder/demo values explicitly labelled.
- [x] Explain measured observations versus modelled estimates and include a footer.
- [x] Keep markup, styles, and scripts in separate files; use accessible labels and unique IDs.
- [x] Review Phase 1 in a browser and record any gaps before advancing.

**Exit check:** All listed page sections exist, paths and controls are wired to their intended placeholders, and demo content cannot be mistaken for live readings.

## Phase 2 — Interactive map

**Status:** Complete
**Goal:** Add the Delhi map experience while preserving the distinction between observations and estimates.

- [x] Integrate Leaflet and OpenStreetMap tiles and centre the initial view on Delhi.
- [x] Add pan/zoom controls and a readable legend.
- [x] Prepare station markers and an estimated-area display using clearly labelled demo data only, until real sources are integrated.
- [x] Keep map behavior in a dedicated map module.
- [x] Review map behavior and labels before advancing.

**Exit check:** Map loads and responds to controls; observed and estimated/demo information is visually distinct.

## Phase 3 — AQI dashboard

**Status:** Complete
**Goal:** Show air-quality values and their provenance clearly.

- [x] Display AQI and category, PM2.5, and PM10.
- [x] Display the default Delhi view and approximate map-centre coordinates.
- [x] Provide source and timestamp status; unavailable live values are clearly identified.
- [x] Provide a data-status or coverage indicator; do not invent confidence or accuracy.
- [x] Label every placeholder value as demo data.

**Exit check:** Dashboard fields are understandable, traceable to a source/status, and do not imply unsupported precision.

## Phase 4 — Search and device location

**Status:** Complete — Nominatim selected by the project owner
**Goal:** Let people select a location and understand the result.

- [x] Integrate OpenStreetMap Nominatim for manually submitted searches; do not add autocomplete.
- [x] Implement browser geolocation from the Use My Location control; request permission only after user action.
- [x] Implement geolocation permission, loading, success, timeout, and error feedback, plus geocoder loading, result, no-result, and service-error states.
- [x] Update selected place/device location, map, and dashboard context together; hide Delhi-only demo overlays for other locations.
- [x] Keep location behavior in a dedicated module.
- [x] Disclose that searches are sent to Nominatim and warn users not to enter private/confidential information.
- [x] Throttle requests per page and cache repeated queries in memory.

**Exit check:** Search and geolocation states are usable, errors are explained, and the selected location stays synchronized.

## Phase 5 — Data source and backend contract

**Status:** In progress — frontend wired to the jointly confirmed v1 contract; connected UI empty-state review and live readings remain open.
**Goal:** Establish trustworthy inputs and a real API contract before presenting live data.

- [ ] Confirm data providers, permissions, fields, units, timestamp conventions, and refresh expectations with the project team.
- [x] Record and wire the backend teammate's proposed health, observation, and prediction contract; finalize/sign off jointly.
- [ ] Implement backend ingestion and quality checks for source, station, coordinates, pollutant, units, and timestamp.
- [ ] Document missing values, duplicates, outliers, and freshness behavior.
- [x] Add a frontend API module for health, observations, and predictions; use relative paths by default and allow a configured API origin.
- [x] Handle loading, unavailable, empty, and failure responses without fabricating measurements.
- [ ] Verify successful integration against a reachable backend and confirm CORS/routing.
- [ ] Before public deployment or increased traffic, proxy public Nominatim searches through a backend with shared caching/rate limiting, or select a provider suited to app-wide usage.

**Exit check:** Frontend and backend agree on a documented contract, and displayed live values retain their source and timestamp.

## Phase 6 — Spatial estimation and validation

**Status:** Not started
**Goal:** Produce estimates only through a documented and evaluated method.

- [ ] Establish a simple explainable baseline such as inverse-distance weighting where data support it.
- [ ] Compare more complex models only when justified by data and evaluation.
- [ ] Validate with held-out locations, spatial block validation, or leave-one-station-out testing.
- [ ] Report appropriate metrics such as MAE, RMSE, and bias, with method and evaluation context.
- [ ] Show coverage/limitations; do not imply estimates are measurements or that a location is safe.

**Exit check:** Any estimate shown in the product is tied to a documented method and validation; unsupported outputs remain labelled demo or are withheld.

## Phase 7 — Integration and product quality

**Status:** Not started
**Goal:** Make the complete experience reliable and accessible across devices.

- [ ] Integrate the frontend and backend on the agreed application structure.
- [ ] Verify mobile and desktop layouts.
- [ ] Check semantic HTML, keyboard operation, labels, and readable contrast.
- [ ] Check loading, error, and empty states, plus measured/estimated/demo labels.
- [ ] Verify asset paths, script loading, and element IDs.
- [ ] Review the integrated application before deployment work.

**Exit check:** Core flows work across supported layouts and failure states, and data integrity principles are visible in the UI.

## Phase 8 — Deployment

**Status:** Not started
**Goal:** Deploy one complete AirSync application using the agreed hosting architecture.

- [ ] Agree the merged branch and final frontend/backend layout.
- [ ] Configure the chosen Vercel routing/runtime for the actual backend implementation.
- [ ] Confirm relative API routes work in the deployed app and configure required environment values safely.
- [ ] Check current hosting limits against model size and inference time.
- [ ] Verify the deployed homepage and API health/prediction routes.
- [ ] Record deployment URL, branch, and any known limitations here.

**Exit check:** The complete app is deployed from the agreed source with frontend and API routes verified.

## Phase log

| Phase | Status | Review notes |
|---|---|---|
| Project audit and checklist | Complete | Workspace inventoried and phased plans recorded. |
| 1. UI foundation | Complete | Browser preview reviewed at mobile width; demo labels and placeholder control feedback confirmed. |
| 2. Interactive map | Complete | Browser preview confirmed OSM tiles, zoom control, demo marker popup, and visible attribution. |
| 3. AQI dashboard | Complete | Browser review confirmed demo values, approximate map-centre location, demo-fixture source, unavailable timestamp, and unavailable coverage. |
| 4. Search and device location | Complete | Nominatim search and map selection reviewed with a Delhi query. Device permission remains user-triggered and was not invoked during review. |
| 5. Data source and backend contract | In progress | Frontend accepts the contract and backend confirmation is recorded in `docs/API_CONTRACT.md`. Backend health, unavailable observations response, frontend page, and CORS preflight verified. Connected UI empty-state review and live source configuration remain open; AQI stays uncalculated until a scale is selected. |
| 6. Spatial estimation and validation | Not started | |
| 7. Integration and product quality | Not started | |
| 8. Deployment | Not started | |

## Update protocol

1. Work only on the current phase.
2. Check off an item only after it is implemented and reviewed.
3. Add concise evidence or known gaps to that phase's review notes.
4. Move the “next phase” marker only after the current phase meets its exit check.
5. If a dependency is missing, record it and keep dependent items open rather than substituting fabricated data.

For the original scope and product principles, see [AirSync Project Plan](AirSync_Project_Plan.md).
