# AirSync backend deployment preparation

**Status:** Backend entry point is prepared for Vercel. A combined AirSync deployment is not ready because the frontend files, approved live data source, and frontend/backend contract agreement are still missing.

## Current backend layout

- `api/index.py` exports a FastAPI application instance named `app`.
- `requirements.txt` declares FastAPI and Uvicorn.
- `.python-version` pins Python 3.12, matching the local environment and a currently supported Vercel Python version.
- Vercel detects the FastAPI entry point without a routing rewrite; `vercel.json` sets a bounded 30-second function duration for the optional provider calls.
- No frontend `public/` assets, shared persistence service, scheduled ingestion, or validated prediction model exist yet. The ingestion CLI can write a user-selected local JSON snapshot.

Vercel documents automatic FastAPI detection for supported entry points, Python version selection through `.python-version`, and static asset serving from `public/**`. Confirm the configured project's plan/runtime and request duration against live-source latency before enabling provider reads.

The observation route makes at most six sequential provider requests (one location page plus up to five sensor lists), each with a three-second timeout. The 30-second limit leaves response overhead while bounding the function. The route has no shared cache or cross-instance rate limiter, so keep it disabled in public production until a shared request-control strategy is selected and configured.

Vercel's documented Python function bundle limit is 500 MB; keep future model dependencies and assets below the current limit and measure inference duration before adding a prediction route. Function duration limits vary by plan and runtime configuration.

## Environment configuration

Set these in the hosting environment's secret/environment settings; do not commit credentials:

| Variable | Required | Purpose |
|---|---:|---|
| `AIRSYNC_ENABLE_OPENAQ` | No; defaults to false | Explicitly enables upstream OpenAQ calls after provider terms and attribution are reviewed. |
| `OPENAQ_API_KEY` | Only when enabled | Authorized OpenAQ API key. |
| `AIRSYNC_CORS_ORIGINS` | No | Comma-separated exact origins for local frontend development; leave unset for same-origin production routing. |

With the source disabled, `/api/observations` returns an empty unavailable response. `/api/predict` always returns unavailable until an evaluated model is explicitly wired in. The health route remains independent of provider configuration.

## Combined application checklist

1. Add the frontend's agreed static/app structure to this repository.
2. Keep API calls same-origin using `/api/health` and the frontend-approved observation route/schema.
3. Review Vercel framework detection and static asset behavior on the merged repository.
4. Add environment secrets in Vercel only after the source/provider license review.
5. Verify the deployed health and observation routes; do not advertise estimates until the spatial model is evaluated.

## Official references

- [FastAPI on Vercel](https://vercel.com/docs/frameworks/backend/fastapi): recognized app entry points and automatic detection.
- [Python runtime](https://vercel.com/docs/functions/runtimes/python): Python version configuration, ASGI app export, dependency installation, and static asset guidance.
- [Function duration limits](https://vercel.com/docs/functions/limitations): plan-dependent maximum execution time and bundle limits.
- [Configuring maximum duration](https://vercel.com/docs/functions/configuring-functions/duration): `maxDuration` configuration for Python functions when needed.
