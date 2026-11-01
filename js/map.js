const defaultLocation = window.AIRSYNC_CONFIG.defaultLocation;
const mapElement = document.querySelector("#air-map");

if (mapElement && window.L) {
  const airMap = L.map(mapElement, {
    center: [defaultLocation.latitude, defaultLocation.longitude],
    zoom: 11,
    minZoom: 3,
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
  const measuredObservationLayer = L.layerGroup();
  const selectedLocationLayer = L.layerGroup();
  let hasUserSelectedLocation = false;

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

  function setLegendMode(mode) {
    const demoStationLegend = document.querySelector("#demo-station-legend");
    const estimateLegend = document.querySelector("#estimate-area-legend");
    const measuredLegend = document.querySelector("#measured-station-legend");
    const selectedLegend = document.querySelector("#device-location-legend");
    const modeLabel = document.querySelector("#map-data-mode");
    const legendNote = document.querySelector("#map-legend-note");

    demoStationLegend.hidden = mode !== "demo";
    estimateLegend.hidden = mode !== "demo";
    measuredLegend.hidden = mode !== "measured";
    selectedLegend.hidden = mode !== "selected";

    if (mode === "demo") {
      modeLabel.textContent = "DEMO OVERLAYS";
      legendNote.textContent = "No live readings or validated estimates";
    } else if (mode === "measured") {
      modeLabel.textContent = "MEASURED OBSERVATIONS";
      legendNote.textContent = "Select a marker to inspect its source readings";
    } else {
      modeLabel.textContent = "SELECTED LOCATION";
      legendNote.textContent = "No station readings linked to this location";
    }
  }

  function showDemoOverlays() {
    if (hasUserSelectedLocation) {
      return;
    }

    if (airMap.hasLayer(measuredObservationLayer)) {
      airMap.removeLayer(measuredObservationLayer);
    }
    if (!airMap.hasLayer(demoOverlayLayer)) {
      demoOverlayLayer.addTo(airMap);
    }
    setLegendMode("demo");
  }

  function formatTimestamp(value) {
    if (!value) {
      return "Timestamp unavailable";
    }
    const timestamp = new Date(value);
    return Number.isNaN(timestamp.getTime())
      ? "Timestamp unavailable"
      : timestamp.toISOString().replace("T", " ").replace(/\.\d{3}Z$/, " UTC");
  }

  function createObservationPopup(station, observations, collectionSource) {
    const popup = document.createElement("div");
    const title = document.createElement("strong");
    title.className = "map-popup-title";
    title.textContent = station.name || "Measured station";
    popup.append(title);

    const state = document.createElement("span");
    state.className = "map-popup-label";
    state.textContent = "MEASURED SOURCE DATA";
    popup.append(state);

    observations.forEach((observation) => {
      const line = document.createElement("p");
      const reading = observation.value == null ? "Value unavailable" : String(observation.value);
      const unit = observation.unit ? ` ${observation.unit}` : "";
      line.textContent = `${observation.pollutant || "Pollutant"}: ${reading}${unit} · ${formatTimestamp(observation.observed_at)}`;
      popup.append(line);
    });

    const provenance = document.createElement("span");
    const provider = observations.find((item) => item.provider)?.provider;
    const source = observations.find((item) => item.source)?.source || collectionSource;
    provenance.textContent = [provider, source].filter(Boolean).join(" · ") || "Source not provided";
    popup.append(provenance);

    const attributionValue = observations.find((item) => item.attribution)?.attribution;
    if (attributionValue) {
      const attribution = document.createElement("p");
      attribution.textContent = Array.isArray(attributionValue)
        ? attributionValue.join(" · ")
        : String(attributionValue);
      popup.append(attribution);
    }

    return popup;
  }

  function showMeasuredObservations(observations, collectionSource) {
    const stationGroups = new Map();

    observations
      .filter((observation) => observation?.status === "measured" && observation.station)
      .forEach((observation) => {
        const latitude = Number(observation.station.latitude);
        const longitude = Number(observation.station.longitude);
        if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
          return;
        }

        const key = observation.station.id || `${latitude},${longitude}`;
        const existing = stationGroups.get(key);
        if (existing) {
          existing.observations.push(observation);
        } else {
          stationGroups.set(key, {
            station: { ...observation.station, latitude, longitude },
            observations: [observation],
          });
        }
      });

    if (stationGroups.size === 0 || hasUserSelectedLocation) {
      showDemoOverlays();
      return 0;
    }

    if (airMap.hasLayer(demoOverlayLayer)) {
      airMap.removeLayer(demoOverlayLayer);
    }
    measuredObservationLayer.clearLayers();

    stationGroups.forEach(({ station, observations: stationObservations }) => {
      const marker = L.circleMarker([station.latitude, station.longitude], {
        radius: 8,
        color: "#fffefa",
        weight: 3,
        fillColor: "#557a60",
        fillOpacity: 1,
      }).addTo(measuredObservationLayer);

      marker.bindPopup(createObservationPopup(station, stationObservations, collectionSource));
      marker.on("click", () => {
        window.dispatchEvent(
          new CustomEvent("airsync:stationselect", {
            detail: { station, observations: stationObservations, source: collectionSource },
          }),
        );
      });
    });

    measuredObservationLayer.addTo(airMap);
    setLegendMode("measured");
    return stationGroups.size;
  }

  let selectedLocationMarker;
  window.addEventListener("airsync:locationchange", ({ detail }) => {
    const position = [Number(detail.latitude), Number(detail.longitude)];
    if (!position.every(Number.isFinite)) {
      return;
    }

    hasUserSelectedLocation = true;
    airMap.setView(position, 13);

    [demoOverlayLayer, measuredObservationLayer, selectedLocationLayer].forEach((layer) => {
      if (airMap.hasLayer(layer)) {
        airMap.removeLayer(layer);
      }
    });
    selectedLocationLayer.clearLayers();

    selectedLocationMarker = L.circleMarker(position, {
      radius: 8,
      color: "#fffefa",
      weight: 3,
      fillColor: "#3f7190",
      fillOpacity: 1,
    }).addTo(selectedLocationLayer);

    const popupContent = document.createElement("div");
    const popupTitle = document.createElement("strong");
    popupTitle.className = "map-popup-title";
    popupTitle.textContent = detail.label || "Selected location";
    const popupMessage = document.createElement("span");
    popupMessage.textContent =
      "The displayed air-quality values are not a current measurement for this location.";
    popupContent.append(popupTitle, popupMessage);
    selectedLocationMarker.bindPopup(popupContent);
    selectedLocationLayer.addTo(airMap);

    setLegendMode("selected");
    document.querySelector("#selected-location-legend-label").textContent =
      detail.source === "device" ? "Your device location" : "Selected place";
    mapElement.setAttribute(
      "aria-label",
      "Interactive map centred on the selected location. Air-quality values depend on backend data availability.",
    );
  });

  window.airSyncMap = Object.freeze({ showMeasuredObservations, showDemoOverlays });
}
