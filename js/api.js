const apiConfiguration = window.AIRSYNC_CONFIG;

function apiUrl(path) {
  const baseUrl = String(apiConfiguration.apiBaseUrl || "").replace(/\/+$/, "");
  return `${baseUrl}${path}`;
}

async function requestJson(path) {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), 10000);

  try {
    const response = await fetch(apiUrl(path), {
      headers: { Accept: "application/json" },
      signal: controller.signal,
    });

    let payload;
    try {
      payload = await response.json();
    } catch {
      throw new Error("The API returned an unreadable response.");
    }

    if (!response.ok) {
      const serverMessage =
        payload && typeof payload === "object" && typeof payload.message === "string"
          ? payload.message
          : null;
      throw new Error(
        serverMessage || `The API request failed (${response.status}).`,
      );
    }

    return payload;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("The API request timed out. Please try again later.");
    }
    if (error instanceof TypeError) {
      throw new Error("The API could not be reached. Check the configured backend address and connection.");
    }
    throw error;
  } finally {
    window.clearTimeout(timeoutId);
  }
}

function getHealth() {
  return requestJson("/api/health");
}

function getObservations(maxLocations = apiConfiguration.observationLimit) {
  const boundedLimit = Math.min(5, Math.max(1, Number.parseInt(maxLocations, 10) || 3));
  return requestJson(`/api/observations?max_locations=${boundedLimit}`);
}

function getPrediction(latitude, longitude, pollutant) {
  const query = new URLSearchParams({
    latitude: String(latitude),
    longitude: String(longitude),
    pollutant,
  });
  return requestJson(`/api/predict?${query.toString()}`);
}

window.airSyncApi = Object.freeze({ getHealth, getObservations, getPrediction });
