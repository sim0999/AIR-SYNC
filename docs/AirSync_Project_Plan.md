# AirSync --- Hyperlocal Air Quality Mapping

## 1. Project Overview

**Project name:** AirSync\
**Project type:** Hyperlocal air-quality mapping web application\
**Initial focus area:** Delhi, India\
**Frontend stack:** HTML, CSS, JavaScript\
**Backend stack:** FastAPI (Python)\
**Deployment target:** Vercel\
**Repository:** `airsync`

AirSync aims to make air-quality information more useful at a local
level. City-wide AQI summaries can hide meaningful differences between
nearby locations---for example, a busy traffic junction and a greener
residential lane.

The project explores combining ground monitoring observations with
supporting information such as weather and land use, then using spatial
modelling to estimate air quality in locations that are not directly
monitored.

**Important:** The map must clearly distinguish measured observations
from modelled estimates. Demonstration or simulated readings must be
labelled as such. Do not present demo data as real-world measurements or
claim model accuracy before validation.

## 2. Problem Statement

### City-wide averages do not tell the whole story

-   Monitoring stations measure pollution at fixed locations.
-   Areas between stations are not directly observed.
-   Air pollution can vary from one street or neighbourhood to another.
-   A single city-wide AQI label may not represent the conditions at an
    individual's location.

AirSync aims to provide clearer local context while transparently
showing where information is measured and where it is estimated.

## 3. Proposed Solution

Build an interactive web application that:

-   Displays air-quality monitoring stations on a map.
-   Supports searching for a location and using the user's current
    location.
-   Shows AQI, PM2.5, PM10, source information, and timestamps where
    available.
-   Explores spatial estimates for areas between monitoring stations.
-   Labels measured and estimated data distinctly.
-   Communicates data freshness and coverage limitations.
-   Connects to a FastAPI backend and a future ML prediction pipeline.

## 4. Core Users and Use Cases

Potential users include:

-   Residents checking air quality near home.
-   Parents and caregivers considering outdoor activities.
-   People who exercise outdoors and want local context.
-   People who want to compare locations within Delhi.
-   Researchers and civic groups exploring local pollution patterns.

These are intended use cases; the project should not make medical claims
or guarantee that an estimated location is safe.

## 5. Data and Modelling Concept

The proposed research workflow is:

1.  **Data sources:** Ground observations from CPCB/DPCC and potentially
    OpenAQ, with weather and geographic information where reliable and
    available.
2.  **Ingestion:** Collect values with source, station identifier,
    coordinates, pollutant, units, and timestamp.
3.  **Quality control:** Standardise units and timestamps, inspect
    outliers, remove duplicates, and document missing readings.
4.  **Spatial features:** Consider coordinates, distance to stations,
    weather, roads, and land use when trustworthy data are available.
5.  **Modelling:** Start with an explainable baseline such as
    inverse-distance weighting (IDW); compare ML approaches such as
    Random Forest and potentially XGBoost/CatBoost only when
    appropriate.
6.  **Validation:** Use held-out locations, spatial block
    cross-validation, or leave-one-station-out testing. Report suitable
    metrics such as MAE, RMSE, and bias.
7.  **Map output:** Show observed stations and estimated areas with
    clear labels, data freshness, and support/coverage information.

Do not assume a more complex model is automatically better. Do not
invent confidence values or accuracy metrics. If uncertainty intervals
are not available, show a transparent coverage indicator instead.

The original project presentation describes the current interface
prototype as using simulated demonstration readings; real monitoring
data and validated model outputs are planned rather than already
established.

## 6. Frontend Development Plan

Build the frontend in phases. Work on one phase at a time and review it
in the browser before moving on.

### Phase 1 --- UI Foundation

Create a responsive AirSync website with:

-   AirSync branding and navigation.
-   Hero heading: **"Breathe Better. Know Your Air."**
-   Brief project description.
-   Location search input.
-   Search button and "Use My Location" button.
-   AQI summary area.
-   Map container.
-   Measured-versus-estimated explanation.
-   Footer.

Keep HTML, CSS, and JavaScript in separate files.

### Phase 2 --- Interactive Map

-   Integrate Leaflet with OpenStreetMap tiles.
-   Centre the initial map on Delhi.
-   Support zooming and panning.
-   Prepare station markers and estimated-area display.
-   Add map controls and a legend.
-   Visually distinguish observed readings from estimates.
-   Keep map implementation in `map.js`.

### Phase 3 --- AQI Dashboard

Prepare display components for:

-   AQI value and category.
-   PM2.5.
-   PM10.
-   Selected location.
-   Coordinates, where appropriate.
-   Data source.
-   Last updated timestamp.
-   Data status or coverage indicator.

Use labelled demo values until real data is available.

### Phase 4 --- Search and Location

-   Allow users to enter a location.
-   Add browser geolocation through "Use My Location."
-   Show location permission, loading, and error states.
-   Update the selected location and map.
-   Do not invent a geocoding service or API key; leave integration
    configurable until a provider is selected.

### Phase 5 --- FastAPI Integration

-   Create a dedicated `api.js` module.
-   Use relative API paths such as `/api/predict`.
-   Avoid hardcoding `localhost` in deployed frontend code.
-   Handle loading, successful responses, empty results, and errors.
-   Match the frontend's data fields to the actual FastAPI response
    contract.
-   Do not fabricate real AQI or model output.

### Phase 6 --- Polish and Testing

-   Responsive layouts for mobile and desktop.
-   Accessible labels and semantic HTML.
-   Readable contrast and keyboard-friendly controls.
-   Loading indicators, error messages, and empty states.
-   Clear measured/estimated labels.
-   Verify all file paths and element IDs.
-   Test with Live Server and then test the deployed application.

## 7. Frontend Repository Structure

The frontend development branch can use:

``` text
airsync/
└── public/
    ├── index.html
    ├── css/
    │   └── style.css
    ├── js/
    │   ├── app.js
    │   ├── map.js
    │   ├── dashboard.js
    │   ├── location.js
    │   └── api.js
    └── assets/
        └── logo.svg
```

### File responsibilities

-   `index.html`: Semantic page structure and section containers.
-   `style.css`: Layout, typography, colors, responsive styling.
-   `app.js`: App startup and coordination.
-   `map.js`: Leaflet map, markers, map controls, and legend.
-   `dashboard.js`: AQI and pollutant display updates.
-   `location.js`: Search and browser geolocation.
-   `api.js`: Calls to the FastAPI backend and response/error handling.
-   `assets/`: Logo and other static assets.

It is fine to begin with only `index.html`, `style.css`, and `app.js`,
then create the other modules when their phases begin.

## 8. Backend Branch and Final Combined Structure

Frontend and backend may be developed on separate Git branches:

-   `front-end`: frontend work.
-   `backend`: FastAPI and ML work.
-   `main`: the merged, complete application used for deployment.

A possible backend branch structure:

``` text
backend/
├── api/
│   └── index.py
├── ml/
│   ├── predict.py
│   └── preprocessing.py
└── requirements.txt
```

After merging, the final deployment structure must be agreed with the
backend developer and configured for the selected hosting approach.
Separate Git branches do not automatically combine into one deployment;
merge the required work into `main` first.

## 9. Vercel Deployment Goal

The goal is **one complete AirSync app deployment**, not separately
hosted frontend and backend websites.

For a lightweight Vercel setup, the FastAPI application can serve the
frontend and API under the same domain, or the project can use Vercel's
supported combined-service setup. The exact routing and file layout must
match the final backend implementation.

Desired user-facing routes may include:

-   `/` --- AirSync frontend.
-   `/api/health` --- backend health check.
-   `/api/predict` --- prediction endpoint.
-   `/docs` --- FastAPI API documentation, if enabled.

The frontend should call relative API paths such as `/api/predict`.
Check current Vercel runtime and size/time limits before deploying a
large or slow ML model. Heavy inference may require a separate runtime
even if the user-facing app is presented under one domain.

## 10. Codex Prompt --- Build the Project in Phases

Use the following instruction as the main Codex project prompt:

> Build the AirSync frontend using HTML, CSS, and JavaScript.
>
> AirSync is a hyperlocal air-quality mapping website initially focused
> on Delhi. It aims to provide more local context than city-wide AQI
> averages by displaying monitoring stations and, in a future validated
> workflow, estimates for locations between stations.
>
> Work through these phases:
>
> 1.  UI foundation: branding, navigation, hero, location search, AQI
>     summary, map container, measured-versus-estimated explanation,
>     footer.
> 2.  Interactive map: Leaflet and OpenStreetMap, Delhi map, markers,
>     legend, map controls, clear observed/estimated distinction.
> 3.  AQI dashboard: AQI, category, PM2.5, PM10, location, source,
>     timestamp, and coverage/status information.
> 4.  Location features: search and browser geolocation with permission,
>     loading, and error states.
> 5.  FastAPI integration: create `api.js`, use relative endpoints such
>     as `/api/predict`, match the actual backend response, and handle
>     errors.
> 6.  Polish: responsive layout, accessibility, testing, and clear data
>     labels.
>
> Keep files organized under `public/`:
>
> -   `index.html`
> -   `css/style.css`
> -   `js/app.js`
> -   `js/map.js`
> -   `js/dashboard.js`
> -   `js/location.js`
> -   `js/api.js`
> -   `assets/`
>
> Do not create or change backend files; the teammate is handling
> FastAPI and ML. Do not claim simulated data is real or invent model
> accuracy. Build one phase at a time, preserve existing work, and
> explain which files were changed.

## 11. Starter HTML Prompt

> Create `public/index.html` for AirSync, a responsive hyperlocal
> air-quality mapping website.
>
> Include a navbar with AirSync branding and Overview, Explore Map, and
> About links. Add a hero section with "Breathe Better. Know Your Air."
> and a concise description. Add a location search input, Search button,
> and Use My Location button. Include an AQI summary, a map container, a
> measured-versus-estimated explanation, and a footer.
>
> Use semantic HTML5. Link `css/style.css` and `js/app.js` using correct
> relative paths. Keep CSS and JavaScript outside the HTML. Use
> accessible labels and unique IDs. Do not create a backend. Do not
> present demo readings as real measurements.

## 12. Development and Git Workflow

### Preview locally

1.  Open the project folder in VS Code.
2.  Install the Live Server extension.
3.  Right-click `index.html` and choose **Open with Live Server**.
4.  Remember: Live Server previews frontend files; it does not run
    FastAPI.

### Branch commands

Fetch GitHub branches:

``` bash
git fetch origin
git branch -a
```

Switch to an existing local branch:

``` bash
git switch front-end
```

Create a local branch tracking the GitHub branch, if it is not already
local:

``` bash
git switch -c front-end --track origin/front-end
```

Save and push frontend changes:

``` bash
git add .
git commit -m "Build AirSync frontend phase"
git push origin front-end
```

Merge the frontend and backend branches into `main` when the combined
app is ready. Vercel should deploy the merged, complete project from the
configured branch.

## 13. Product and Data Integrity Principles

-   Clearly label measured data and modelled estimates.
-   Label simulated readings as demo data.
-   Display source and timestamp when available.
-   Do not claim a location is safe based only on an estimate.
-   Do not claim model accuracy before rigorous validation.
-   Show coverage or limitations when uncertainty is not quantified.
-   Do not silently invent missing measurements.
-   Keep the interface understandable for non-technical users.

## 14. Project Goal

Deliver a clear, responsive AirSync web application that helps users
explore local air-quality context. The frontend should be easy to
develop independently, integrate cleanly with the teammate's FastAPI
backend, and ultimately deploy as one complete application.
