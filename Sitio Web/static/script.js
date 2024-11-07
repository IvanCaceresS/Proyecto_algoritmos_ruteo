// Inicializar el mapa centrado en las coordenadas dadas
var map = L.map("map").setView([-33.454868, -70.644747], 13);
// Añadir el tile layer de OpenStreetMap
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution:
    '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(map);
// Definir variables para almacenar las capas
var infraestructuraLayer,
  dijkstraLayer,
  estacionamientosLayer,
  velocidadesLayer,
  precipitacionesLayer,
  inundacionesLayer;
var precipitacionesData = {};

var startIcon = L.icon({
  iconUrl: "../static/Simbologia/inicio.png",
  iconSize: [16, 16],
});
var endIcon = L.icon({
  iconUrl: "../static/Simbologia/meta.png",
  iconSize: [16, 16],
});

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

// DIJKSTRA
fetch("../static/dijkstra.geojson")
  .then((response) => response.json())
  .then((data) => {
    // Definir la capa de Dijkstra
    dijkstraLayer = L.geoJSON(data, {
      style: {
        color: "#FF4500",
        weight: 6,
        opacity: 0.9,
      },
      pointToLayer: function (feature, latlng) {
        if (feature.properties.role === "source") {
          return L.marker(latlng, { icon: startIcon }).bindPopup(
            "Inicio de la ruta"
          );
        } else if (feature.properties.role === "target") {
          return L.marker(latlng, { icon: endIcon }).bindPopup(
            "Final de la ruta"
          );
        }
        return L.circleMarker(latlng, {
          radius: 4,
          color: "#FF4500",
          fillOpacity: 0.8,
        });
      },
    });
    document
      .getElementById("toggle-dijkstra")
      .addEventListener("click", function () {
        toggleLayer(dijkstraLayer);
      });
  })
  .catch((error) => console.error("Error cargando dijkstra.geojson:", error));


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

// Función para determinar el color según el valor de precipitación
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
  
  // Primero, cargamos el archivo JSON de precipitaciones
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
      precipitacionesLayer = L.geoJSON(data, {
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
    .catch((error) => console.error("Error cargando los datos de precipitaciones o inundaciones:", error));

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
                dataSeguridad[comuna] !== undefined ? dataSeguridad[comuna] : "Sin datos";
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
  if (layer) {
    if (map.hasLayer(layer)) {
      map.removeLayer(layer);
    } else {
      map.addLayer(layer);
    }
  } else {
    console.warn("La capa no está definida.");
  }
}