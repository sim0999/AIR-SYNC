# AirSync

AirSync is a hyperlocal air-quality mapping project initially focused on Delhi. The repository currently contains the backend service foundation and project documentation. No live data source or validated prediction model is configured.

## Backend setup

Requires Python 3.10 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn api.index:app --reload
```

The API listens at `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/docs` for the generated OpenAPI page. `GET /api/health` confirms that the process responds; it does not indicate that an observation source or prediction model is available.

For a frontend running on a separate local port, set `AIRSYNC_CORS_ORIGINS` to the exact local origin(s), such as `http://127.0.0.1:5500,http://localhost:5500`. The default is same-origin only; production should use same-origin routing.

### Frontend on another computer on your local network

Start the API bound to the network interfaces, and allow only the exact origin serving the frontend. For example, if the frontend is served at `http://localhost:5500` in the frontend developer's browser:

```powershell
$env:AIRSYNC_CORS_ORIGINS = "http://localhost:5500,http://127.0.0.1:5500"
python -m uvicorn api.index:app --reload --host 0.0.0.0 --port 8000
```

Find the backend computer's private IPv4 address with `ipconfig`, then set the frontend's `apiBaseUrl` to `http://<backend-private-ip>:8000` (for example, `http://192.168.1.25:8000`). The address can change when the network reconnects. Both computers need a route to each other, and the backend computer's firewall must allow inbound TCP traffic on port 8000. Do not use `0.0.0.0` as the frontend URL; it is only the server bind address.

## Optional OpenAQ ingestion

The OpenAQ v3 adapter is opt-in and requires an API key from an authorized OpenAQ account. In PowerShell, set `$env:OPENAQ_API_KEY` before invoking the adapter. Never commit the key. Review the upstream provider/license attribution before using returned observations.

```powershell
$env:OPENAQ_API_KEY = "<your authorized key>"
python -m api.ingestion
```

This performs one bounded fetch and prints normalized JSON to the console. Use `python -m api.ingestion --output data/delhi_latest.json` to save a local snapshot (the `data/` folder is ignored by Git). It is not a scheduled job. See [backend data quality notes](docs/BACKEND_DATA_QUALITY.md) for validation and freshness behavior.

After obtaining a trusted snapshot with sufficient stations, evaluate the IDW baseline by pollutant/unit group using leave-one-station-out validation:

```powershell
python -m api.modeling data/delhi_latest.json --max-age-minutes 180 --max-time-spread-minutes 30 --support-radius-km 10
```

Those limits are example run settings, not approved freshness or spatial-coverage policy. Evaluation output is specific to the snapshot and settings; it is not a general accuracy guarantee.

## Deployment preparation

The backend entry point is prepared for Vercel's FastAPI runtime. The combined application is not deployment-ready until the frontend files and shared API contract are integrated. See [backend deployment notes](docs/BACKEND_DEPLOYMENT.md).

## API contract status

The health route, `/api/observations`, and `/api/predict` are implemented. The prediction route returns an explicit unavailable state until a model is validated. The API envelope remains a proposal until the frontend and backend agree on fields, units, timestamps, status values, empty results, and errors. See [the proposed contract](docs/BACKEND_API_CONTRACT.md).

Live OpenAQ reads are disabled by default. Enable them only after reviewing OpenAQ's terms and each underlying provider's attribution/license, then set `AIRSYNC_ENABLE_OPENAQ=true` and `OPENAQ_API_KEY` in the runtime environment. Each observations request makes bounded upstream calls, has no cache, and should not be polled continuously.

## Data integrity

Do not present demo data as measured observations. Preserve source, station, coordinates, pollutant, unit, timestamp, and measured/estimated status for real results. No data provider, ingestion pipeline, or validated model is currently configured.
