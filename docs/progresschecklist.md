# AirSync Project Progress Checklist

**Last reviewed:** 2026-11-01  
**Working branch:** `backend`
**Rule:** Keep implementation and status evidence current. When the user authorizes multi-phase work, advance independent pieces together and leave dependent items open.

## Current project snapshot

- [x] Reviewed the repository contents, existing project plan, and Git state.
- [x] Recorded an implementation checklist organized into sequential phases.
- [ ] Frontend implementation (not started).

The current checkout is on `backend`. The repository now includes a FastAPI service with health and observations routes, a gated OpenAQ v3 adapter/CLI, draft response schemas, an unevaluated IDW and leave-one-station-out helper, and Vercel backend preparation. There are still no frontend source files, no authorized OpenAQ key, no ingested observations, no validated estimates, and no combined deployment. The backend-specific status and evidence are tracked in [Backend Progress Checklist](BACKEND_PROGRESS_CHECKLIST.md).

## Phase 1 — UI foundation

**Status:** Not started  
**Goal:** Build the semantic, responsive page shell described in the project plan.

- [ ] Add AirSync branding and navigation.
- [ ] Add the hero heading, project introduction, location search, Search, and Use My Location controls.
- [ ] Add initial AQI summary and map container, with any placeholder/demo values explicitly labelled.
- [ ] Explain measured observations versus modelled estimates and include a footer.
- [ ] Keep markup, styles, and scripts in separate files; use accessible labels and unique IDs.
- [ ] Review Phase 1 in a browser and record any gaps before advancing.

**Exit check:** All listed page sections exist, paths and controls are wired to their intended placeholders, and demo content cannot be mistaken for live readings.

## Phase 2 — Interactive map

**Status:** Not started  
**Goal:** Add the Delhi map experience while preserving the distinction between observations and estimates.

- [ ] Integrate Leaflet and OpenStreetMap tiles and centre the initial view on Delhi.
- [ ] Add pan/zoom, map controls, and a readable legend.
- [ ] Prepare station markers and an estimated-area display using clearly labelled demo data only, until real sources are integrated.
- [ ] Keep map behavior in a dedicated map module.
- [ ] Review map behavior and labels before advancing.

**Exit check:** Map loads and responds to controls; observed and estimated/demo information is visually distinct.

## Phase 3 — AQI dashboard

**Status:** Not started  
**Goal:** Show air-quality values and their provenance clearly.

- [ ] Display AQI and category, PM2.5, and PM10.
- [ ] Display selected location and coordinates where useful.
- [ ] Provide source and last-updated time when available.
- [ ] Provide a data-status or coverage indicator; do not invent confidence or accuracy.
- [ ] Label every placeholder value as demo data.

**Exit check:** Dashboard fields are understandable, traceable to a source/status, and do not imply unsupported precision.

## Phase 4 — Search and device location

**Status:** Not started  
**Goal:** Let people select a location and understand the result.

- [ ] Implement location search with a configurable geocoding provider; do not invent a provider or API key.
- [ ] Implement browser geolocation from the Use My Location control.
- [ ] Show permission, loading, success, empty-result, and error states.
- [ ] Update the selected location and map together.
- [ ] Keep location behavior in a dedicated module.

**Exit check:** Search and geolocation states are usable, errors are explained, and the selected location stays synchronized.

## Phase 5 — Data source and backend contract

**Status:** Backend foundation and API proposal implemented; frontend integration and live-source activation remain pending.

**Goal:** Establish trustworthy inputs and a real API contract before presenting live data.

- [ ] Confirm data providers, permissions, fields, units, timestamp conventions, and refresh expectations with the project team.
- [x] Define a proposed FastAPI response contract for health and observations; frontend agreement remains pending.
- [x] Implement an opt-in OpenAQ adapter and quality checks for source, station, coordinates, pollutant, units, and timestamp.
- [x] Document missing values, duplicates, outliers, and freshness behavior; live data source authorization remains pending.
- [ ] Add a frontend API module using relative paths such as `/api/predict`.
- [ ] Handle loading, success, empty, and failure responses without fabricating measurements.

**Exit check:** Frontend and backend agree on a documented contract, and displayed live values retain their source and timestamp.

## Phase 6 — Spatial estimation and validation

**Status:** Baseline and validation helpers implemented; not evaluated because no trusted observations are available.

**Goal:** Produce estimates only through a documented and evaluated method.

- [x] Add an explainable IDW baseline helper with explicit support/freshness requirements; it is not exposed by the API.
- [x] Document model inputs, units, assumptions, and support limitations.
- [ ] Compare more complex models only when justified by data and evaluation.
- [x] Add leave-one-station-out and MAE/RMSE/bias calculation helpers.
- [x] Add a snapshot-based evaluation command that reports metrics by pollutant and unit.
- [ ] Run spatial holdout evaluation; no evaluation has been run without observations.
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

**Status:** Backend deployment preparation documented; no combined deployment has been performed.

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
| Project audit and checklist | Complete | Repository and backend branch inspected. |
| 1. UI foundation | Not started | Next phase. |
| 2. Interactive map | Not started | |
| 3. AQI dashboard | Not started | |
| 4. Search and device location | Not started | |
| 5. Data source and backend contract | Partial | API envelope and opt-in OpenAQ adapter exist; no key/records and no frontend agreement. |
| 6. Spatial estimation and validation | Partial (unevaluated) | IDW and leave-one-station-out metric helpers exist; no estimates or metrics reported. |
| 7. Integration and product quality | Not started | Frontend files are not present. |
| 8. Deployment | Prepared (backend only) | Vercel backend configuration documented; combined app not deployed. |

## Update protocol

1. Prefer phase order; when the user authorizes multi-phase work, advance independent pieces together and leave dependent items open.
2. Check off an item only after it is implemented and reviewed.
3. Add concise evidence or known gaps to that phase's review notes.
4. Move the “next phase” marker only after the current phase meets its exit check.
5. If a dependency is missing, record it and keep dependent items open rather than substituting fabricated data.

For the original scope and product principles, see [AirSync Project Plan](AirSync_Project_Plan.md).
