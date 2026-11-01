# AirSync Frontend — Branch Checklist

This document is for the person working on the `frontend` branch in the frontend workspace. Work through one phase at a time: finish its checklist, review it, and update the status before starting the next phase.

## Current status

- **Branch:** `frontend`
- **Workspace reviewed:** `C:\Users\ry105\OneDrive\Desktop\New folder\AIR-SYNC`
- **Current phase:** Phase 1 — UI foundation
- **Phase 1 status:** Not started
- **Audit finding:** The workspace has an empty root `index.html`, a minimal `README.md`, and project documentation. No frontend CSS or JavaScript implementation is present yet.

## Phase 1 — UI foundation

**Status:** Not started

- [ ] Create the semantic page structure and AirSync branding/navigation.
- [ ] Add the “Breathe Better. Know Your Air.” hero and concise project description.
- [ ] Add location search, Search, and Use My Location controls.
- [ ] Add an AQI summary and map container.
- [ ] Explain measured observations versus modelled estimates; include the footer.
- [ ] Keep HTML, CSS, and JavaScript separate; use accessible labels and unique IDs.
- [ ] Label all sample values as demo data; do not imply measurements are live.
- [ ] Preview and review this phase before moving on.

**Exit check:** All page sections exist, assets/scripts load, and demo content is clearly identified.

## Phase 2 — Interactive map

**Status:** Not started

- [ ] Integrate Leaflet with OpenStreetMap and centre the map on Delhi.
- [ ] Add pan/zoom controls and a readable legend.
- [ ] Add clearly labelled demo station markers and an estimated-area treatment.
- [ ] Visually distinguish observed, estimated, and demo information.
- [ ] Keep map behavior in a dedicated module.
- [ ] Review map behavior before moving on.

**Exit check:** The map works and the legend makes each data type clear.

## Phase 3 — AQI dashboard

**Status:** Not started

- [ ] Show AQI/category, PM2.5, and PM10.
- [ ] Show selected location and coordinates where useful.
- [ ] Show source, timestamp, and status/coverage when available.
- [ ] Label demo values and avoid invented accuracy/confidence claims.

**Exit check:** Every displayed value has an honest status and provenance or is explicitly demo content.

## Phase 4 — Search and device location

**Status:** Not started

- [ ] Integrate a geocoding provider only after it is selected/configured by the team.
- [ ] Add browser geolocation to Use My Location.
- [ ] Show permission, loading, success, no-result, and error states.
- [ ] Keep selected location and map in sync.

**Exit check:** Search and device location handle expected states without hardcoded secrets or fabricated results.

## Phase 5 — Backend API integration

**Status:** Not started; depends on the backend response contract being agreed.

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
| 1. UI foundation | Not started | Current phase |
| 2. Interactive map | Not started | |
| 3. AQI dashboard | Not started | |
| 4. Search and device location | Not started | |
| 5. Backend API integration | Blocked on contract | Agree JSON fields/routes with backend developer |
| 6. Accessibility and integration readiness | Not started | |

## Branch coordination rules

- Do frontend work and commits on `frontend`; do not commit backend implementation on this branch.
- Keep UI structure and styling independent of backend internals.
- Agree API paths, field names, units, timestamps, and status labels with the backend developer before integration.
- Use demo fixtures only when clearly labelled; never present them as real air-quality observations.
- Merge branches only when both sides are ready and the integration structure has been agreed.

See [AirSync Project Plan](AirSync_Project_Plan.md) for product scope and data-integrity principles, and [Backend Progress Checklist](BACKEND_PROGRESS_CHECKLIST.md) for the other branch's work plan and starter prompt.
