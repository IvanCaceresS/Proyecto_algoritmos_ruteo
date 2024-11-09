var map = L.map("map", {
  center: [-33.454868, -70.644747],
  zoom: 13,
  zoomControl: true,
}).whenReady(() => {
  console.log("Mapa cargado completamente.");
});

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution:
    '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(map);

var startIcon = L.icon({
  iconUrl: "../static/Simbologia/inicio.png", 
  iconSize: [16, 16],
});
var endIcon = L.icon({
  iconUrl: "../static/Simbologia/meta.png",
  iconSize: [16, 16],
});

var userMarker = null;
var nearestNodeMarker = null;
var endMarker = null;
var selectingStart = true;
var autoStartSet = false; 

// Función de cálculo de distancia entre dos puntos
function calculateDistance(lat1, lng1, lat2, lng2) {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) *
      Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)); // Definir correctamente la variable `c`
  return R * c;
}

// Función para encontrar el nodo más cercano
function findNearestNode(lat, lng, icon, popupText) {
  return fetch("../static/Archivos_exportados/infraestructura_nodos.geojson")
    .then((response) => response.json())
    .then((data) => {
      let nearestNode = null;
      let minDistance = Infinity;

      data.features.forEach((feature) => {
        const [nodeLng, nodeLat] = feature.geometry.coordinates;
        const distance = calculateDistance(lat, lng, nodeLat, nodeLng);

        if (distance < minDistance) {
          minDistance = distance;
          nearestNode = feature;
        }
      });

      if (nearestNode) {
        const nearestNodeId = nearestNode.properties.id;
        const [nearestNodeLng, nearestNodeLat] =
          nearestNode.geometry.coordinates;

        L.marker([nearestNodeLat, nearestNodeLng], { icon: icon })
          .addTo(map)
          .bindPopup(popupText + " más cercano, nodo ID: " + nearestNodeId)
          .openPopup();

        return nearestNodeId;
      }
    })
    .catch((error) =>
      console.log("Error al cargar el archivo GeoJSON:", error)
    );
}

// Habilitar ubicación manual para el usuario
function enableManualLocation() {
  console.log("Función enableManualLocation activada.");
  if (selectingStart) {
    alert(
      "Por favor, haz clic en el mapa para seleccionar tu ubicación inicial."
    );
  }
  map.on("click", function (e) {
    const lat = e.latlng.lat;
    const lng = e.latlng.lng;

    if (selectingStart) {
      if (userMarker) map.removeLayer(userMarker);
      userMarker = L.marker([lat, lng], { icon: startIcon })
        .addTo(map)
        .bindPopup("Ubicación de inicio seleccionada")
        .openPopup();

      findNearestNode(lat, lng, startIcon, "Punto de inicio").then(
        (nearestNodeId) => {
          nearestNodeMarker = { nodeId: nearestNodeId };
          selectingStart = false;
          alert("Ahora selecciona la ubicación de fin.");
        }
      );
    } else {
      if (endMarker) map.removeLayer(endMarker);
      endMarker = L.marker([lat, lng], { icon: endIcon })
        .addTo(map)
        .bindPopup("Ubicación de fin seleccionada")
        .openPopup();

      findNearestNode(lat, lng, endIcon, "Punto de fin").then(
        (nearestNodeId) => {
          nearestNodeMarkerEnd = { nodeId: nearestNodeId };

          map.off("click");
          alert(
            "Has seleccionado ambos puntos. Ahora se calcularán las rutas."
          );
          console.log("Punto de inicio:", nearestNodeMarker.nodeId);
          console.log("Punto de fin:", nearestNodeMarkerEnd.nodeId);
          dijkstra();
          cplex();
          dijkstraComplete();
        }
      );
    }
  });
}

// Función para manejar geolocalización y seleccionar nodo más cercano como punto inicial
function handleGeolocation(position) {
  const lat = position.coords.latitude;
  const lng = position.coords.longitude;
  map.setView([lat, lng], 13);

  // Agregar marcador de ubicación geolocalizada del usuario
  if (userMarker) map.removeLayer(userMarker);
  userMarker = L.marker([lat, lng])
    .addTo(map)
    .bindPopup("Tu ubicación actual")
    .openPopup();

  findNearestNode(lat, lng, startIcon, "Punto de inicio").then(
    (nearestNodeId) => {
      nearestNodeMarker = { nodeId: nearestNodeId };
      autoStartSet = true;
      alert(
        "Ubicación de inicio definida automáticamente. Ahora selecciona el destino."
      );
      selectingStart = false;
      enableManualLocation();
    }
  );
}
// Función para cargar y mostrar la ruta en el mapa
function loadRouteOnMap(data, routeType = "dijkstra") {
  if (!data) {
    console.error("No se proporcionó ningún dato GeoJSON.");
    return;
  }

  if (!window.routeLayers) {
    window.routeLayers = {};
  }

  // Determinar el color basado en el tipo de ruta
  const colorMap = {
    dijkstra: "#FF4500",
    cplex: "#0000FF",
    dijkstra_complete: "#32CD32", // Color para Dijkstra Completa
  };
  const color = colorMap[routeType] || "#FF4500";

  // Crear y añadir la capa de la ruta al mapa
  window.routeLayers[routeType] = L.geoJSON(data, {
    style: {
      color: color,
      weight: 6,
      opacity: 0.9,
    },
    pointToLayer: function (feature, latlng) {
      if (feature.properties.role === "source") {
        return L.marker(latlng, { icon: startIcon }).bindPopup("Inicio de la ruta");
      } else if (feature.properties.role === "target") {
        return L.marker(latlng, { icon: endIcon }).bindPopup("Final de la ruta");
      }
      return L.circleMarker(latlng, {
        radius: 4,
        color: color,
        fillOpacity: 0.8,
      });
    },
  }).addTo(map);

  // Agregar el evento al botón para alternar la visibilidad de la capa
  const toggleButtonId = `toggle-${routeType}`;
  document
    .getElementById(toggleButtonId)
    .addEventListener("click", function () {
      toggleLayer(window.routeLayers[routeType]);
    });
}

// Función para llamar al backend y calcular la ruta
function dijkstra() {
  var tiempoInicial = new Date().getTime();
  console.log("Calculando la ruta Dijkstra...");
  fetch("/dijkstra", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      start_id: nearestNodeMarker.nodeId,
      end_id: nearestNodeMarkerEnd.nodeId,
    }),
  })
    .then((response) => (response.ok ? response.json() : Promise.reject(response.statusText)))
    .then((data) => {
      if (data.success) {
        var tiempoFinal = new Date().getTime();
        var tiempoTotal = tiempoFinal - tiempoInicial;
        document.getElementById("ruta-dijkstra").textContent =
          "Ruta (Dijkstra) - Tiempo total: " + tiempoTotal + " ms";
        loadRouteOnMap(data.geojson, "dijkstra");
      } else {
        alert("No se pudo calcular la ruta.");
      }
    })
    .catch((error) => console.error("Error al calcular la ruta Dijkstra:", error));
}

// Función para llamar al backend y calcular la ruta CPLEX
function cplex() {
  var tiempoInicial = new Date().getTime();
  console.log("Calculando la ruta usando CPLEX...");
  fetch("/cplex", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      start_id: nearestNodeMarker.nodeId,
      end_id: nearestNodeMarkerEnd.nodeId,
    }),
  })
    .then((response) => (response.ok ? response.json() : Promise.reject(response.statusText)))
    .then((data) => {
      if (data.success) {
        var tiempoFinal = new Date().getTime();
        var tiempoTotal = tiempoFinal - tiempoInicial;
        document.getElementById("ruta-cplex").textContent =
          "Ruta (CPLEX) - Tiempo total: " + tiempoTotal + " ms";
        loadRouteOnMap(data.geojson, "cplex");
      } else {
        alert("No se pudo calcular la ruta usando CPLEX.");
      }
    })
    .catch((error) => console.error("Error al calcular la ruta usando CPLEX:", error));
}

// Función para llamar al backend y calcular la ruta Dijkstra Completa
function dijkstraComplete() {
  var tiempoInicial = new Date().getTime();
  console.log("Calculando la ruta Dijkstra Completa...");
  fetch("/dijkstra_complete", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      start_id: nearestNodeMarker.nodeId,
      end_id: nearestNodeMarkerEnd.nodeId,
    }),
  })
    .then((response) => (response.ok ? response.json() : Promise.reject(response.statusText)))
    .then((data) => {
      if (data.success) {
        var tiempoFinal = new Date().getTime();
        var tiempoTotal = tiempoFinal - tiempoInicial;
        document.getElementById("ruta-dijkstra-completa").textContent =
          "Ruta (Dijkstra Completa) - Tiempo total: " + tiempoTotal + " ms";
        loadRouteOnMap(data.geojson, "dijkstra_complete");
      } else {
        alert("No se pudo calcular la ruta Dijkstra Completa.");
      }
    })
    .catch((error) => console.error("Error al calcular la ruta Dijkstra Completa:", error));
}


// Verificar si la geolocalización está disponible y establecer el nodo inicial automáticamente si es posible
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(handleGeolocation, function (error) {
    console.log("Geolocalización no permitida o disponible:", error);
    selectingStart = true;
    enableManualLocation();
  });
} else {
  console.log("Geolocalización no soportada en este navegador.");
  selectingStart = true;
  enableManualLocation();
}

// INFRAESTRUCTURA
fetch("../static/Archivos_exportados/infraestructura.geojson")
  .then((response) => response.json())
  .then((data) => {
    infraestructuraLayer = L.geoJSON(data, {
      style: {
        color: "#505050",
        weight: 2,
        opacity: 0.8,
      },
    });
    document
      .getElementById("toggle-infraestructura")
      .addEventListener("click", function () {
        toggleLayer(infraestructuraLayer);
      });
  })
  .catch((error) =>
    console.error("Error cargando infraestructura.geojson:", error)
  );

// CICLOVÍAS
fetch("../static/Archivos_exportados/ciclovias.geojson")
  .then((response) => response.json())
  .then((data) => {
    cicloviaLayer = L.geoJSON(data, {
      style: {
        color: "#A90DBA",
        weight: 2,
        opacity: 0.8,
      },
    });
    document
      .getElementById("toggle-ciclovias")
      .addEventListener("click", function () {
        toggleLayer(cicloviaLayer);
      });
  })
  .catch((error) => console.error("Error cargando ciclovias.geojson:", error));

// INFRAESTRUCTURA NODOS
fetch("../static/Archivos_exportados/infraestructura_nodos.geojson")
  .then((response) => response.json())
  .then((data) => {
    infraestructuraNodosLayer = L.geoJSON(data, {
      pointToLayer: function (feature, latlng) {
        return L.circleMarker(latlng, {
          radius: 4,
          fillColor: "black",
          color: "black",
          weight: 1,
          opacity: 1,
          fillOpacity: 0.9,
        });
      },
      onEachFeature: function (feature, layer) {
        if (feature.properties && feature.properties.id) {
          layer.bindPopup("Nodo ID: " + feature.properties.id);
        }
      },
    });
    document
      .getElementById("toggle-infraestructura-nodos")
      .addEventListener("click", function () {
        toggleLayer(infraestructuraNodosLayer);
      });
  })
  .catch((error) =>
    console.error("Error cargando infraestructura_nodos.geojson:", error)
  );

// ILUMINACIÓN
fetch("../static/Archivos_exportados/iluminacion.geojson")
  .then((response) => response.json())
  .then((data) => {
    iluminacionLayer = L.geoJSON(data, {
      style: function (feature) {
        var lit = feature.properties.lit;
        var color;
        if (lit === "yes") {
          color = "yellow";
        } else {
          color = "gray";
        }
        return {
          color: color,
          weight: 4,
          opacity: 0.9,
        };
      },
    });
    document
      .getElementById("toggle-iluminacion")
      .addEventListener("click", function () {
        toggleLayer(iluminacionLayer);
      });
  })
  .catch((error) =>
    console.error("Error cargando iluminacion.geojson:", error)
  );

// ESTACIONAMIENTOS
fetch("../static/Archivos_exportados/estacionamientos.geojson")
  .then((response) => response.json())
  .then((data) => {
    var estacionamientoIcon = L.divIcon({
      html: `
            <svg class="estacionamiento-icono" width="24" height="24" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
                <g fill="none" stroke="green" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="18" cy="46" r="12"/>
                    <circle cx="46" cy="46" r="12"/>
                    <path d="M18 46h28l-8-16h-12l4 8h-4"/>
                    <path d="M36 30l-6-10h-8"/>
                    <circle cx="26" cy="20" r="2"/>
                </g>
            </svg>
        `,
      className: "",
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });
    estacionamientosLayer = L.geoJSON(data, {
      pointToLayer: function (feature, latlng) {
        return L.marker(latlng, { icon: estacionamientoIcon });
      },
      onEachFeature: function (feature, layer) {
        if (feature.properties && feature.properties.name) {
          layer.bindPopup(feature.properties.name);
        }
      },
    });
    document
      .getElementById("toggle-estacionamientos")
      .addEventListener("click", function () {
        toggleLayer(estacionamientosLayer);
      });
  })
  .catch((error) =>
    console.error("Error cargando estacionamientos.geojson:", error)
  );

// VELOCIDADES MÁXIMAS
fetch("../static/Archivos_exportados/velocidades_maximas.geojson")
  .then((response) => response.json())
  .then((data) => {
    velocidadesLayer = L.geoJSON(data, {
      style: function (feature) {
        var maxspeed = feature.properties.maxspeed;
        var color;
        if (maxspeed === "50") {
          color = "red";
        } else if (maxspeed === "40") {
          color = "blue";
        } else {
          color = "gray";
        }
        return {
          color: color,
          weight: 4,
          opacity: 0.9,
        };
      },
    });
    document
      .getElementById("toggle-velocidades")
      .addEventListener("click", function () {
        toggleLayer(velocidadesLayer);
      });
  })
  .catch((error) =>
    console.error("Error cargando velocidades_maximas.geojson:", error)
  );

// PRECIPITACIONES
function getColorPrecipitation(value) {
  return value === null
    ? "gray"
    : value > 10
    ? "#00008b"
    : value > 5
    ? "#4169e1"
    : value >= 0
    ? "#add8e6"
    : "gray";
}
var precipitacionesData = {};
fetch("../static/Archivos_exportados/precipitacion_comunas_rm.json")
  .then((response) => response.json())
  .then((data) => {
    data.forEach(function (entry) {
      precipitacionesData[entry.comuna] = parseFloat(entry.precip_mm);
    });
    return fetch("../static/Archivos_exportados/inundaciones.geojson");
  })
  .then((response) => response.json())
  .then((data) => {
    var precipitacionesLayer = L.geoJSON(data, {
      style: function (feature) {
        var comuna = feature.properties.nom_comuna;
        var precipValue = precipitacionesData[comuna];
        return {
          fillColor: getColorPrecipitation(precipValue),
          weight: 2,
          opacity: 1,
          color: "black",
          fillOpacity: 0.7,
        };
      },
      onEachFeature: function (feature, layer) {
        var comuna = feature.properties.nom_comuna;
        var precipValue =
          precipitacionesData[comuna] !== undefined
            ? precipitacionesData[comuna]
            : "Sin datos";
        var popupContent =
          "<strong>Comuna:</strong> " +
          comuna +
          "<br>" +
          "<strong>Precipitación:</strong> " +
          precipValue +
          " mm";
        layer.bindPopup(popupContent);
      },
    });
    document
      .getElementById("toggle-precipitacion")
      .addEventListener("click", function () {
        toggleLayer(precipitacionesLayer);
      });
  })
  .catch((error) =>
    console.error(
      "Error cargando los datos de precipitaciones o inundaciones:",
      error
    )
  );

// RIESGO DE INUNDACIONES
function getColor(d) {
  return d === null
    ? "gray"
    : d > 0.05
    ? "#FF0000"
    : d > 0.03
    ? "#FF8C00"
    : d > 0.01
    ? "#FFD700"
    : d > 0
    ? "#9ACD32"
    : "#00FF00";
}
fetch("../static/Archivos_exportados/inundaciones.geojson")
  .then((response) => response.json())
  .then((data) => {
    inundacionesLayer = L.geoJSON(data, {
      style: function (feature) {
        var riesgo = feature.properties.ind_riesgo_inundaciones_t10_delta;
        return {
          fillColor: getColor(riesgo),
          weight: 2,
          opacity: 1,
          color: "black",
          fillOpacity: 0.7,
        };
      },
      onEachFeature: function (feature, layer) {
        var popupContent =
          "<strong>Comuna:</strong> " +
          feature.properties.nom_comuna +
          "<br>" +
          "<strong>Riesgo de Inundación:</strong> " +
          (feature.properties.ind_riesgo_inundaciones_t10_delta !== null
            ? feature.properties.ind_riesgo_inundaciones_t10_delta
            : "Sin datos");
        layer.bindPopup(popupContent);
      },
    });
    document
      .getElementById("toggle-inundaciones")
      .addEventListener("click", function () {
        toggleLayer(inundacionesLayer);
      });
  })
  .catch((error) =>
    console.error("Error cargando inundaciones.geojson:", error)
  );

// INDICE DE SEGURIDAD
function getColorSeguridad(value) {
  return value === null
    ? "gray"
    : value >= 900
    ? "#FF0000"
    : value >= 660
    ? "#FF8C00"
    : value >= 350
    ? "#FFD700"
    : "#00FF00";
}
fetch("../static/Archivos_exportados/seguridad_comunas_rm.json")
  .then((response) => response.json())
  .then((dataSeguridad) => {
    return fetch("../static/Archivos_exportados/inundaciones.geojson")
      .then((response) => response.json())
      .then((dataInundaciones) => {
        seguridadLayer = L.geoJSON(dataInundaciones, {
          style: function (feature) {
            var comuna = feature.properties.nom_comuna;
            var value = parseFloat(dataSeguridad[comuna]);
            return {
              fillColor: getColorSeguridad(value),
              weight: 2,
              opacity: 1,
              color: "black",
              fillOpacity: 0.7,
            };
          },
          onEachFeature: function (feature, layer) {
            var comuna = feature.properties.nom_comuna;
            var value =
              dataSeguridad[comuna] !== undefined
                ? dataSeguridad[comuna]
                : "Sin datos";
            var popupContent =
              "<strong>Comuna:</strong> " +
              comuna +
              "<br>" +
              "<strong>Índice de Seguridad:</strong> " +
              value;
            layer.bindPopup(popupContent);
          },
        });
        document
          .getElementById("toggle-seguridad")
          .addEventListener("click", function () {
            toggleLayer(seguridadLayer);
          });
      })
      .catch((error) =>
        console.error("Error cargando inundaciones.geojson:", error)
      );
  })
  .catch((error) =>
    console.error("Error cargando seguridad_comunas_rm.json:", error)
  );

// CIERRE DE CALLES
function getColorCierre(roadClosure) {
  return roadClosure === "Yes"
    ? "#FF0000"
    : roadClosure === "No"
    ? "#00FF00"
    : "gray";
}
fetch("../static/Archivos_exportados/cierres_calles.json")
  .then((response) => response.json())
  .then((dataCierres) => {
    return fetch("../static/Archivos_exportados/infraestructura.geojson")
      .then((response) => response.json())
      .then((dataInfraestructura) => {
        cierreCallesLayer = L.geoJSON(dataInfraestructura, {
          style: function (feature) {
            var streetName = feature.properties.name;
            var roadClosureData = dataCierres.find(
              (street) => street.name === streetName
            );
            var roadClosure = roadClosureData
              ? roadClosureData.road_closure
              : "Sin datos";
            return {
              fillColor: getColorCierre(roadClosure),
              weight: 2,
              opacity: 1,
              color: getColorCierre(roadClosure),
              fillOpacity: 0.7,
            };
          },
          onEachFeature: function (feature, layer) {
            var streetName = feature.properties.name;
            var roadClosureData = dataCierres.find(
              (street) => street.name === streetName
            );
            var roadClosure = roadClosureData
              ? roadClosureData.road_closure
              : "Sin datos";
            var popupContent =
              "<strong>Calle:</strong> " +
              streetName +
              "<br>" +
              "<strong>Cierre de Calle:</strong> " +
              roadClosure;
            layer.bindPopup(popupContent);
          },
        });
        document
          .getElementById("toggle-cierres")
          .addEventListener("click", function () {
            toggleLayer(cierreCallesLayer);
          });
      })
      .catch((error) =>
        console.error("Error cargando infraestructura.geojson:", error)
      );
  })
  .catch((error) =>
    console.error("Error cargando cierres_calles.json:", error)
  );

// TRÁFICO ACTUAL
function getTrafficColor(speed) {
  return speed <= 20
    ? "#FF0000"
    : speed <= 30
    ? "#FFA500"
    : speed <= 40
    ? "#FFFF00"
    : "#00FF00";
}
fetch("../static/Archivos_exportados/trafico_actual.json")
  .then((response) => response.json())
  .then((dataTrafico) => {
    return fetch("../static/Archivos_exportados/infraestructura.geojson")
      .then((response) => response.json())
      .then((dataInfraestructura) => {
        traficoLayer = L.geoJSON(dataInfraestructura, {
          style: function (feature) {
            var streetName = feature.properties.name;
            var trafficData = dataTrafico.find(
              (street) => street.name === streetName
            );
            var speed = trafficData ? trafficData.current_speed : null;
            return {
              color: speed !== null ? getTrafficColor(speed) : "gray",
              weight: 3,
              opacity: 0.8,
            };
          },
          onEachFeature: function (feature, layer) {
            var streetName = feature.properties.name;
            var trafficData = dataTrafico.find(
              (street) => street.name === streetName
            );
            var speed = trafficData ? trafficData.current_speed : "Sin datos";
            var popupContent =
              "<strong>Calle:</strong> " +
              streetName +
              "<br>" +
              "<strong>Velocidad Actual:</strong> " +
              speed +
              " km/h";
            layer.bindPopup(popupContent);
          },
        });
        document
          .getElementById("toggle-trafico")
          .addEventListener("click", function () {
            toggleLayer(traficoLayer);
          });
      })
      .catch((error) =>
        console.error("Error cargando infraestructura.geojson:", error)
      );
  })
  .catch((error) =>
    console.error("Error cargando trafico_actual.json:", error)
  );

// Añadir control de capas al mapa
document
  .getElementById("toggle-simbologia-btn")
  .addEventListener("click", function () {
    var simbologia = document.getElementById("simbologia");
    if (simbologia.style.display === "none" || !simbologia.style.display) {
      simbologia.style.display = "block";
    } else {
      simbologia.style.display = "none";
    }
  });
// Función para mostrar u ocultar una capa
function toggleLayer(layer) {
  if (layer !== undefined) {
    if (map.hasLayer(layer)) {
      map.removeLayer(layer);
    } else {
      map.addLayer(layer);
    }
  } else {
    console.warn("La capa no está definida.");
    //Informa al usuario que la capa, con su nombre no está definida por una alerta
    alert("La capa no está definida.");
  }
}
