const delhiCenter = [28.6139, 77.209];
const mapElement = document.querySelector("#air-map");

if (mapElement && window.L) {
  const airMap = L.map(mapElement, {
    center: delhiCenter,
    zoom: 11,
    minZoom: 9,
    maxZoom: 18,
    scrollWheelZoom: false,
    zoomControl: true,
    keyboard: true,
  });

  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(airMap);

  const demoOverlayLayer = L.layerGroup().addTo(airMap);
  const estimateZone = L.polygon(
    [
      [28.665, 77.145],
      [28.68, 77.225],
      [28.625, 77.29],
      [28.575, 77.245],
      [28.59, 77.17],
    ],
    {
      className: "estimate-area",
      color: "#9d8654",
      weight: 2,
      dashArray: "7 6",
      fillColor: "#b89b64",
      fillOpacity: 0.12,
    },
  ).addTo(demoOverlayLayer);

  estimateZone.bindPopup(
    '<strong class="map-popup-title">Illustrative estimate area</strong><span>This outline is a visual demo only. It is not a model output, coverage boundary, or validated estimate.</span><br><span class="map-popup-label">DEMO OVERLAY</span>',
  );

  const demoStationIcon = L.divIcon({
    className: "demo-station-icon",
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -12],
  });

  const demoPoints = [
    { label: "Demo point A", coordinates: [28.681, 77.222] },
    { label: "Demo point B", coordinates: [28.632, 77.219] },
    { label: "Demo point C", coordinates: [28.589, 77.233] },
  ];

  demoPoints.forEach(({ label, coordinates }) => {
    L.marker(coordinates, { icon: demoStationIcon })
      .addTo(demoOverlayLayer)
      .bindPopup(
        `<strong class="map-popup-title">${label}</strong><span>Illustrative marker only. No monitoring station or air-quality reading is represented here.</span><br><span class="map-popup-label">DEMO MARKER</span>`,
      );
  });

  let selectedLocationMarker;
  window.addEventListener("airsync:locationchange", ({ detail }) => {
    const position = [detail.latitude, detail.longitude];
    if (!position.every(Number.isFinite)) {
      return;
    }

    airMap.setView(position, 13);

    if (selectedLocationMarker) {
      selectedLocationMarker.remove();
    }

    selectedLocationMarker = L.circleMarker(position, {
      radius: 8,
      color: "#fffefa",
      weight: 3,
      fillColor: "#3f7190",
      fillOpacity: 1,
    }).addTo(airMap);

    const popupContent = document.createElement("div");
    const popupTitle = document.createElement("strong");
    popupTitle.className = "map-popup-title";
    popupTitle.textContent = detail.label || "Selected location";
    const popupMessage = document.createElement("span");
    popupMessage.textContent =
      "The displayed air-quality values are demo data and do not describe current conditions here.";
    popupContent.append(popupTitle, popupMessage);
    selectedLocationMarker.bindPopup(popupContent);

    if (airMap.hasLayer(demoOverlayLayer)) {
      airMap.removeLayer(demoOverlayLayer);
    }

    document.querySelector("#demo-station-legend").hidden = true;
    document.querySelector("#estimate-area-legend").hidden = true;
    document.querySelector("#device-location-legend").hidden = false;
    document.querySelector("#selected-location-legend-label").textContent =
      detail.source === "device" ? "Your device location" : "Selected place";
    document.querySelector("#map-legend-note").textContent =
      "No air-quality measurements for this location";
    mapElement.setAttribute(
      "aria-label",
      "Interactive map centred on the selected location. Air-quality information is demo-only.",
    );
  });
}
