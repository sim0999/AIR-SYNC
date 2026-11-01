"""Shared response models for the AirSync API proposal."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


class Station(BaseModel):
    id: str
    name: str | None = None
    latitude: float = Field(allow_inf_nan=False, ge=-90, le=90)
    longitude: float = Field(allow_inf_nan=False, ge=-180, le=180)
    sensor_id: str | None = None


class Attribution(BaseModel):
    name: str | None = None
    attribution_name: str | None = None
    attribution_url: str | None = None


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["measured", "estimated", "demo"]
    pollutant: str = Field(min_length=1)
    value: float = Field(allow_inf_nan=False, ge=0)
    unit: str = Field(min_length=1)
    observed_at: datetime
    source: str = Field(min_length=1)
    provider: str | None = None
    station: Station
    attribution: list[Attribution] = Field(default_factory=list)
    coverage: dict[str, Any] | None = None

    @field_validator("observed_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must include a timezone offset")
        return value


class ObservationCollection(BaseModel):
    status: Literal["measured", "unavailable"]
    source: str | None = None
    observations: list[Observation] = Field(default_factory=list)
    message: str | None = None

    @model_validator(mode="after")
    def validate_collection_status(self) -> "ObservationCollection":
        if self.status == "measured" and not self.observations:
            raise ValueError("A measured collection must contain at least one observation.")
        if self.status == "unavailable" and self.observations:
            raise ValueError("An unavailable collection cannot contain observations.")
        if any(item.status != "measured" for item in self.observations):
            raise ValueError("The observations endpoint may contain measured records only.")
        if self.observations and not self.source:
            raise ValueError("A measured collection must identify its source.")
        return self


class PredictionValue(BaseModel):
    value: float = Field(allow_inf_nan=False, ge=0)
    unit: str = Field(min_length=1)


class PredictionResponse(BaseModel):
    status: Literal["estimated", "unavailable"]
    latitude: float = Field(allow_inf_nan=False, ge=-90, le=90)
    longitude: float = Field(allow_inf_nan=False, ge=-180, le=180)
    pollutant: str = Field(min_length=1)
    prediction: PredictionValue | None = None
    method: str | None = None
    coverage: dict[str, Any] | None = None
    message: str

    @model_validator(mode="after")
    def validate_prediction_status(self) -> "PredictionResponse":
        if self.status == "estimated" and (self.prediction is None or not self.method):
            raise ValueError("An estimated response must include a prediction and method.")
        if self.status == "unavailable" and self.prediction is not None:
            raise ValueError("An unavailable response cannot include a prediction.")
        return self


class APIError(BaseModel):
    code: str
    message: str
    field_errors: list[dict[str, str]] | None = None


class APIErrorResponse(BaseModel):
    error: APIError
