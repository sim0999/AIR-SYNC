const locationLabels = {
  header: document.querySelector("#header-location-label"),
  heading: document.querySelector("#map-title"),
  current: document.querySelector("#current-location-value"),
  detail: document.querySelector("#current-location-detail"),
  latitude: document.querySelector("#location-latitude"),
  longitude: document.querySelector("#location-longitude"),
  disclaimer: document.querySelector("#data-disclaimer"),
};

window.addEventListener("airsync:locationchange", ({ detail }) => {
  const latitudeDirection = detail.latitude >= 0 ? "N" : "S";
  const longitudeDirection = detail.longitude >= 0 ? "E" : "W";

  const selectedLabel = detail.label || "Selected location";
  locationLabels.header.textContent = selectedLabel;
  locationLabels.heading.textContent =
    detail.source === "device" ? "Map around your location" : `Map around ${selectedLabel}`;
  locationLabels.current.textContent = selectedLabel;
  locationLabels.detail.textContent =
    detail.source === "device" ? "Selected from this device" : "Selected via OpenStreetMap Nominatim";
  locationLabels.latitude.textContent = `${Math.abs(detail.latitude).toFixed(4)}° ${latitudeDirection}`;
  locationLabels.longitude.textContent = `${Math.abs(detail.longitude).toFixed(4)}° ${longitudeDirection}`;
  locationLabels.disclaimer.textContent =
    `The selected location is shown on the map. Air-quality values remain illustrative demo data and do not describe current conditions there.`;
});
