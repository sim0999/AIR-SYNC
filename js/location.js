const locationForm = document.querySelector("#location-search");
const locationInput = document.querySelector("#location-input");
const locationButton = document.querySelector("#use-location");
const locationMessage = document.querySelector("#search-message");
const locationResults = document.querySelector("#location-results");
const searchButton = locationForm.querySelector('button[type="submit"]');
const geocoder = window.AIRSYNC_CONFIG.geocoder;
const cachedSearches = new Map();
let lastRequestAt = 0;

function setLocationMessage(text) {
  locationMessage.textContent = text;
}

function setSearchBusy(isBusy) {
  searchButton.disabled = isBusy;
  searchButton.setAttribute("aria-busy", String(isBusy));
}

function displayPlaceName(place) {
  return String(place.display_name || "")
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean)
    .slice(0, 3)
    .join(", ") || "Unnamed place";
}

function clearLocationResults() {
  locationResults.replaceChildren();
  locationResults.hidden = true;
}

function selectPlace(place) {
  const latitude = Number(place.lat);
  const longitude = Number(place.lon);

  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
    setLocationMessage("That result did not include usable map coordinates. Try another place.");
    return;
  }

  const label = displayPlaceName(place);
  window.dispatchEvent(
    new CustomEvent("airsync:locationchange", {
      detail: { latitude, longitude, label, source: "nominatim" },
    }),
  );
  setLocationMessage(
    `${label} selected. Air-quality values remain illustrative demo data, not current readings for this place.`,
  );
  clearLocationResults();
}

function renderLocationResults(places) {
  locationResults.replaceChildren();

  places.forEach((place) => {
    const item = document.createElement("li");
    item.className = "location-result-item";

    const button = document.createElement("button");
    button.className = "location-result";
    button.type = "button";

    const name = document.createElement("span");
    name.className = "location-result-name";
    name.textContent = displayPlaceName(place);

    const type = document.createElement("span");
    type.className = "location-result-type";
    type.textContent = String(place.addresstype || place.type || "Place");

    button.append(name, type);
    button.addEventListener("click", () => selectPlace(place));
    item.append(button);
    locationResults.append(item);
  });

  locationResults.hidden = places.length === 0;
}

async function searchPlaces(searchTerm) {
  const cacheKey = searchTerm.toLocaleLowerCase();
  if (cachedSearches.has(cacheKey)) {
    return cachedSearches.get(cacheKey);
  }

  const waitRemaining = geocoder.minimumRequestIntervalMs - (Date.now() - lastRequestAt);
  if (lastRequestAt > 0 && waitRemaining > 0) {
    await new Promise((resolve) => window.setTimeout(resolve, waitRemaining));
  }

  const url = new URL(geocoder.endpoint);
  url.searchParams.set("q", searchTerm);
  url.searchParams.set("format", "jsonv2");
  url.searchParams.set("limit", String(geocoder.resultLimit));

  lastRequestAt = Date.now();
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), 10000);
  let response;
  try {
    response = await fetch(url, {
      headers: { Accept: "application/json" },
      referrerPolicy: "strict-origin-when-cross-origin",
      signal: controller.signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("Place search timed out. Please check your connection and try again.");
    }
    throw new Error("Could not reach OpenStreetMap Nominatim. Check your connection and try again.");
  } finally {
    window.clearTimeout(timeoutId);
  }

  if (response.status === 429) {
    throw new Error("The place search service is busy. Please wait a moment before searching again.");
  }
  if (!response.ok) {
    throw new Error("Place search is temporarily unavailable. Please try again later.");
  }

  const places = await response.json();
  if (!Array.isArray(places)) {
    throw new Error("Place search returned an unexpected response. Please try again later.");
  }

  cachedSearches.set(cacheKey, places);
  return places;
}

locationForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const searchTerm = locationInput.value.trim();

  clearLocationResults();
  if (!searchTerm) {
    setLocationMessage("Enter a place to search.");
    locationInput.focus();
    return;
  }

  setSearchBusy(true);
  setLocationMessage(`Searching ${geocoder.providerName}…`);

  try {
    const places = await searchPlaces(searchTerm);
    if (places.length === 0) {
      setLocationMessage("No matching places found. Try a nearby city, neighbourhood, or postcode.");
    } else {
      renderLocationResults(places);
      setLocationMessage(
        `${places.length} place${places.length === 1 ? "" : "s"} found. Choose one to move the map.`,
      );
    }
  } catch (error) {
    setLocationMessage(
      error instanceof Error
        ? error.message
        : "Place search is temporarily unavailable. Please try again later.",
    );
  } finally {
    setSearchBusy(false);
  }
});

locationButton.addEventListener("click", () => {
  if (!navigator.geolocation) {
    setLocationMessage(
      "This browser does not support device location. You can still search for a place or explore the Delhi map.",
    );
    return;
  }

  locationButton.disabled = true;
  locationButton.setAttribute("aria-busy", "true");
  setLocationMessage("Requesting your device location…");

  navigator.geolocation.getCurrentPosition(
    ({ coords }) => {
      window.dispatchEvent(
        new CustomEvent("airsync:locationchange", {
          detail: {
            latitude: coords.latitude,
            longitude: coords.longitude,
            label: "Your location",
            source: "device",
          },
        }),
      );
      setLocationMessage(
        "Your location is shown on the map. AQI and pollutant values remain demo-only.",
      );
      locationButton.disabled = false;
      locationButton.removeAttribute("aria-busy");
    },
    (error) => {
      const messages = {
        1: "Location permission was not granted. You can still search for a place or explore the Delhi map.",
        2: "Your location could not be determined. Check device location services and try again.",
        3: "The location request timed out. Please try again.",
      };

      setLocationMessage(
        messages[error.code] || "Device location is unavailable right now. Please try again.",
      );
      locationButton.disabled = false;
      locationButton.removeAttribute("aria-busy");
    },
    { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 },
  );
});
