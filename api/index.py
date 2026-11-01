"""FastAPI application entry point for local development."""

import math
import logging
import os

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .ingestion.openaq import (
    OpenAQAuthenticationError,
    OpenAQError,
    OpenAQRateLimitError,
    fetch_delhi_latest,
)
from .schemas import (
    APIErrorResponse,
    HealthResponse,
    Observation as ObservationSchema,
    ObservationCollection,
    PredictionResponse,
)

logger = logging.getLogger("airsync.api")

app = FastAPI(
    title="AirSync API",
    description=(
        "Backend API for AirSync. Air-quality observations and estimates "
        "will be exposed only after their sources and contract are agreed."
    ),
    version="0.1.0",
)

cors_origins = [
    origin.strip()
    for origin in os.getenv("AIRSYNC_CORS_ORIGINS", "").split(",")
    if origin.strip()
]
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["Accept", "Content-Type"],
    )


@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, dict) else {}
    code = detail.get("code") if isinstance(detail.get("code"), str) else "http_error"
    message = detail.get("message") if isinstance(detail.get("message"), str) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": code, "message": message}},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    field_errors = [
        {
            "field": ".".join(str(part) for part in error.get("loc", ())),
            "message": str(error.get("msg", "Invalid value.")),
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "invalid_request",
                "message": "One or more request parameters are invalid.",
                "field_errors": field_errors,
            }
        },
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Hide internal details from clients while the server logs the exception."""
    logger.exception("Unhandled error while processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "An unexpected server error occurred.",
            }
        },
    )


@app.get("/api/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Report that the API process is responding; this does not imply data readiness."""
    return HealthResponse(status="ok", service="airsync-api")


@app.get(
    "/api/observations",
    response_model=ObservationCollection,
    responses={
        422: {"model": APIErrorResponse, "description": "Invalid query parameter."},
        502: {"model": APIErrorResponse, "description": "Upstream source failure."},
        503: {"model": APIErrorResponse, "description": "Source configuration or rate-limit issue."},
        500: {"model": APIErrorResponse, "description": "Unexpected server error."},
    },
    tags=["observations"],
)
def observations(
    max_locations: int = Query(default=3, ge=1, le=5),
) -> ObservationCollection:
    """Return measured observations only when an operator enables OpenAQ."""
    enabled = os.getenv("AIRSYNC_ENABLE_OPENAQ", "").strip().lower() in {"1", "true", "yes"}
    if not enabled:
        return ObservationCollection(
            status="unavailable",
            source=None,
            observations=[],
            message="Live observation source is disabled.",
        )

    api_key = os.getenv("OPENAQ_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "source_credentials_missing",
                "message": "OpenAQ is enabled but OPENAQ_API_KEY is not configured.",
            },
        )

    try:
        report = fetch_delhi_latest(
            api_key,
            max_location_pages=1,
            max_locations=max_locations,
            timeout_seconds=3,
        )
    except OpenAQRateLimitError as exc:
        headers = {"Retry-After": exc.retry_after} if exc.retry_after else None
        raise HTTPException(
            status_code=503,
            detail={"code": "upstream_rate_limited", "message": str(exc)},
            headers=headers,
        ) from exc
    except OpenAQAuthenticationError as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "source_credentials_invalid", "message": str(exc)},
        ) from exc
    except OpenAQError as exc:
        raise HTTPException(
            status_code=502,
            detail={"code": "upstream_source_error", "message": str(exc)},
        ) from exc

    observations = [
        ObservationSchema.model_validate(observation.to_payload())
        for observation in report.observations
    ]
    return ObservationCollection(
        status="measured" if observations else "unavailable",
        source="OpenAQ",
        observations=observations,
        message=(
            f"Limited to at most {max_locations} stations; this is not complete Delhi coverage."
            if observations
            else "OpenAQ returned no valid observations for this request."
        ),
    )


@app.get(
    "/api/predict",
    response_model=PredictionResponse,
    responses={422: {"model": APIErrorResponse, "description": "Invalid prediction query."}},
    tags=["predictions"],
)
def predict(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    pollutant: str = Query(min_length=1, max_length=32),
) -> PredictionResponse:
    """Expose the prediction contract while withholding unvalidated estimates."""
    if (
        not math.isfinite(latitude)
        or not math.isfinite(longitude)
        or not -90 <= latitude <= 90
        or not -180 <= longitude <= 180
    ):
        raise HTTPException(
            status_code=422,
            detail={"code": "invalid_request", "message": "Coordinates must be finite WGS 84 values."},
        )
    pollutant = pollutant.strip()
    if not pollutant:
        raise HTTPException(
            status_code=422,
            detail={"code": "invalid_request", "message": "pollutant must not be blank."},
        )
    return PredictionResponse(
        status="unavailable",
        latitude=latitude,
        longitude=longitude,
        pollutant=pollutant,
        prediction=None,
        method=None,
        coverage=None,
        message="No validated spatial model is available; no estimate is provided.",
    )
