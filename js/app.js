const dashboard = {
  badge: document.querySelector("#data-status-badge"),
  observationLabel: document.querySelector("#observation-status-label"),
  observationMessage: document.querySelector("#observations-message"),
  dataDisclaimer: document.querySelector("#data-disclaimer"),
  dataSource: document.querySelector("#data-source-value"),
  dataSourceDetail: document.querySelector("#data-source-detail"),
  observedTime: document.querySelector("#observed-time-value"),
  observedTimeDetail: document.querySelector("#observed-time-detail"),
  coverage: document.querySelector("#coverage-value"),
  coverageDetail: document.querySelector("#coverage-detail"),
  headerLocation: document.querySelector("#header-location-label"),
  mapHeading: document.querySelector("#map-title"),
  currentLocation: document.querySelector("#current-location-value"),
  currentLocationDetail: document.querySelector("#current-location-detail"),
  latitude: document.querySelector("#location-latitude"),
  longitude: document.querySelector("#location-longitude"),
};

const pollutantRows = {
  pm25: {
    value: document.querySelector("#pm25-value"),
    unit: document.querySelector("#pm25-unit"),
    observation: document.querySelector("#pm25-observation-status"),
    estimate: document.querySelector("#pm25-estimate-status"),
  },
  pm10: {
    value: document.querySelector("#pm10-value"),
    unit: document.querySelector("#pm10-unit"),
    observation: document.querySelector("#pm10-observation-status"),
    estimate: document.querySelector("#pm10-estimate-status"),
  },
};

const defaultLocation = window.AIRSYNC_CONFIG.defaultLocation;
let currentObservationCollection = null;
let predictionRequestSequence = 0;

function setStatusBadge(text) {
  dashboard.badge.lastChild.textContent = ` ${text}`;
}

function resetPollutantRows(observationMessage = "Select a measured station") {
  Object.values(pollutantRows).forEach((row) => {
    row.value.textContent = "—";
    row.unit.textContent = "";
    row.observation.textContent = observationMessage;
    row.estimate.textContent = "Estimate not requested";
  });
}

function normalizePollutantName(name) {
  return String(name || "").toLowerCase().replace(/[^a-z0-9]/g, "");
}

function formatUtcTimestamp(value) {
  if (!value) {
    return "Unavailable";
  }
  const timestamp = new Date(value);
  return Number.isNaN(timestamp.getTime())
    ? "Unavailable"
    : timestamp.toISOString().replace("T", " ").replace(/\.\d{3}Z$/, " UTC");
}

function formatCoverage(coverage) {
  if (coverage == null) {
    return { value: "Not provided", detail: "No coverage summary returned" };
  }
  if (typeof coverage === "string") {
    return { value: coverage, detail: "Coverage reported by backend" };
  }
  if (typeof coverage === "object" && typeof coverage.status === "string") {
    return { value: coverage.status, detail: "Coverage reported by backend" };
  }
  return { value: "Available", detail: "Coverage details returned by backend" };
}

function setCurrentLocation(label, latitude, longitude, sourceDescription) {
  const latitudeDirection = latitude >= 0 ? "N" : "S";
  const longitudeDirection = longitude >= 0 ? "E" : "W";

  dashboard.headerLocation.textContent = label;
  dashboard.currentLocation.textContent = label;
  dashboard.currentLocationDetail.textContent = sourceDescription;
  dashboard.latitude.textContent = `${Math.abs(latitude).toFixed(4)}° ${latitudeDirection}`;
  dashboard.longitude.textContent = `${Math.abs(longitude).toFixed(4)}° ${longitudeDirection}`;
}

function clearSelectedObservation() {
  resetPollutantRows("Select a measured station");
  dashboard.observedTime.textContent = "Unavailable";
  dashboard.observedTimeDetail.textContent = "No station selected";
  dashboard.coverage.textContent = "Not available";
  dashboard.coverageDetail.textContent = "No coverage summary linked to this place";
}

function showCollectionUnavailable(message, source = "Unavailable") {
  currentObservationCollection = null;
  dashboard.observationLabel.textContent = "· NO MEASURED READINGS";
  dashboard.observationMessage.textContent = message || "No measured observations are available.";
  dashboard.dataSource.textContent = source || "Unavailable";
  dashboard.dataSourceDetail.textContent = "No measured station data returned";
  dashboard.dataDisclaimer.textContent =
    "No measured observations are available. Demo map overlays are illustrative only. AQI is not calculated because no scale has been agreed.";
  resetPollutantRows("No measured value selected");
  clearSelectedObservation();
  window.airSyncMap?.showDemoOverlays();
  setStatusBadge("LIVE OBSERVATIONS UNAVAILABLE");
}

function showObservationCollection(collection) {
  currentObservationCollection = collection;
  const observations = Array.isArray(collection?.observations) ? collection.observations : [];
  const measured = observations.filter((observation) => observation?.status === "measured");

  if (collection?.status !== "measured" || measured.length === 0) {
    showCollectionUnavailable(collection?.message, collection?.source || "Unavailable");
    return;
  }

  const source = collection.source || "Source reported per reading";
  const stationCount = window.airSyncMap?.showMeasuredObservations(measured, source) || 0;
  dashboard.observationLabel.textContent = `· ${measured.length} MEASURED READING${measured.length === 1 ? "" : "S"}`;
  dashboard.observationMessage.textContent = stationCount
    ? `Measured readings from ${source}. Select a station marker to inspect its values.`
    : `Measured readings were returned by ${source}, but no usable station coordinates were provided.`;
  dashboard.dataSource.textContent = source;
  dashboard.dataSourceDetail.textContent = "Raw provider values; units are not converted";
  dashboard.observedTime.textContent = "Select a station";
  dashboard.observedTimeDetail.textContent = "Each reading includes its observation time";
  dashboard.coverage.textContent = "Station list";
  dashboard.coverageDetail.textContent = "Up to 3 locations; not complete city coverage";
  dashboard.dataDisclaimer.textContent =
    "Measured observations are shown in the units supplied by the source. AQI is not calculated because the project has not selected a scale.";
  resetPollutantRows("Select a measured station");
  setStatusBadge(`${measured.length} MEASURED READING${measured.length === 1 ? "" : "S"}`);
}

function setSelectedStation(station, observations, collectionSource) {
  const label = station.name || "Measured station";
  const latitude = Number(station.latitude);
  const longitude = Number(station.longitude);
  setCurrentLocation(label, latitude, longitude, "Measured station · source observation");
  dashboard.mapHeading.textContent = `Station: ${label}`;
  dashboard.dataSource.textContent = collectionSource || observations[0]?.source || "Source not provided";
  dashboard.dataSourceDetail.textContent = observations[0]?.provider || "Measured source data";

  Object.entries(pollutantRows).forEach(([key, row]) => {
    const observation = observations.find(
      (item) => item?.status === "measured" && normalizePollutantName(item.pollutant) === key,
    );

    if (!observation || observation.value == null) {
      row.value.textContent = "—";
      row.unit.textContent = "";
      row.observation.textContent = observation
        ? "Measured record has no value"
        : "No reading for this pollutant at this station";
      return;
    }

    row.value.textContent = String(observation.value);
    row.unit.textContent = observation.unit ? ` ${observation.unit}` : "";
    row.observation.textContent = `${observation.pollutant} · measured`;
  });

  const latestObservation = observations
    .filter((item) => item.observed_at)
    .sort((a, b) => new Date(b.observed_at) - new Date(a.observed_at))[0];
  dashboard.observedTime.textContent = formatUtcTimestamp(latestObservation?.observed_at);
  dashboard.observedTimeDetail.textContent = "Source timestamp · UTC";

  const coverage = formatCoverage(observations.find((item) => item.coverage != null)?.coverage);
  dashboard.coverage.textContent = coverage.value;
  dashboard.coverageDetail.textContent = coverage.detail;
  setStatusBadge("MEASURED STATION SELECTED");
  loadPredictions(latitude, longitude);
}

function setPredictionStatus(pollutant, message) {
  const key = normalizePollutantName(pollutant);
  if (pollutantRows[key]) {
    pollutantRows[key].estimate.textContent = message;
  }
}

function displayPrediction(pollutant, response) {
  const key = normalizePollutantName(pollutant);
  const row = pollutantRows[key];
  if (!row) {
    return;
  }

  if (response?.status === "estimated" && response.prediction != null) {
    if (typeof response.unit !== "string" || !response.unit) {
      row.estimate.textContent = "Estimate withheld: backend response has no unit";
      return;
    }
    const method = response.method ? ` · ${response.method}` : "";
    row.estimate.textContent = `Estimate: ${response.prediction} ${response.unit}${method}`;
    return;
  }

  row.estimate.textContent = response?.message || "No validated estimate is available";
}

async function loadPredictions(latitude, longitude) {
  const requestSequence = ++predictionRequestSequence;
  const pollutants = ["PM2.5", "PM10"];
  await Promise.all(
    pollutants.map(async (pollutant) => {
      setPredictionStatus(pollutant, "Checking estimate availability…");
      try {
        const response = await window.airSyncApi.getPrediction(latitude, longitude, pollutant);
        if (requestSequence !== predictionRequestSequence) {
          return;
        }
        displayPrediction(pollutant, response);
      } catch (error) {
        if (requestSequence !== predictionRequestSequence) {
          return;
        }
        setPredictionStatus(
          pollutant,
          error instanceof Error ? error.message : "Prediction service unavailable",
        );
      }
    }),
  );
}

async function initializeBackendData() {
  setStatusBadge("CONNECTING TO BACKEND");
  dashboard.observationMessage.textContent = "Loading backend health and observations…";

  const [healthResult, observationsResult] = await Promise.allSettled([
    window.airSyncApi.getHealth(),
    window.airSyncApi.getObservations(window.AIRSYNC_CONFIG.observationLimit),
  ]);

  if (observationsResult.status === "fulfilled") {
    showObservationCollection(observationsResult.value);
  } else {
    showCollectionUnavailable(
      observationsResult.reason instanceof Error
        ? observationsResult.reason.message
        : "The observations API could not be reached.",
    );
  }

  if (healthResult.status === "rejected" && observationsResult.status === "fulfilled") {
    dashboard.observationMessage.textContent += " Health check did not respond.";
  }

  loadPredictions(defaultLocation.latitude, defaultLocation.longitude);
}

window.addEventListener("airsync:locationchange", ({ detail }) => {
  const label = detail.label || "Selected location";
  const sourceDescription =
    detail.source === "device" ? "Selected from this device" : "Selected via OpenStreetMap Nominatim";

  setCurrentLocation(label, detail.latitude, detail.longitude, sourceDescription);
  dashboard.mapHeading.textContent =
    detail.source === "device" ? "Map around your location" : `Map around ${label}`;
  dashboard.dataSource.textContent = "Not location-matched";
  dashboard.dataSourceDetail.textContent =
    "The observations route does not filter by these coordinates";
  dashboard.dataDisclaimer.textContent =
    "No station readings are linked to this selected place. Any available station list is separate; AQI remains uncalculated.";
  clearSelectedObservation();
  loadPredictions(detail.latitude, detail.longitude);
});

window.addEventListener("airsync:stationselect", ({ detail }) => {
  setSelectedStation(detail.station, detail.observations, detail.source);
});

initializeBackendData();
