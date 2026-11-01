window.AIRSYNC_CONFIG = Object.freeze({
  // Leave empty for same-origin API routes in a combined deployment.
  // Backend developer's LAN address; use same-origin routing in a combined deployment.
  apiBaseUrl: "http://192.168.160.226:8000",
  observationLimit: 3,
  defaultLocation: Object.freeze({
    latitude: 28.6139,
    longitude: 77.209,
    label: "Delhi, India",
  }),
  geocoder: Object.freeze({
    endpoint: "https://nominatim.openstreetmap.org/search",
    providerName: "OpenStreetMap Nominatim",
    resultLimit: 5,
    minimumRequestIntervalMs: 1100,
  }),
});
