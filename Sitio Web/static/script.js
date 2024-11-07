
// Inicializar el mapa centrado en las coordenadas dadas
var map = L.map('map').setView([-33.454868, -70.644747], 13);

// Añadir el tile layer de OpenStreetMap
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

// Definir variables para almacenar las capas
var infraestructuraLayer, dijkstraLayer, estacionamientosLayer, velocidadesLayer;

var startIcon = L.icon({
    iconUrl: '../static/Simbologia/inicio.png',
    iconSize: [16, 16]
});

var endIcon = L.icon({
    iconUrl: '../static/Simbologia/meta.png',
    iconSize: [16, 16]
});

    // Cargar y mostrar el archivo GeoJSON de infraestructura
    fetch('../static/Archivos_exportados/infraestructura.geojson')
    .then(response => response.json())
    .then(data => {
        infraestructuraLayer = L.geoJSON(data, {
            style: {
                color: '#505050',
                weight: 2,
                opacity: 0.8
            }
        })
        //.addTo(map);
    })
    .catch(error => console.error('Error cargando infraestructura.geojson:', error));

// Cargar y mostrar el archivo GeoJSON de nodos de infraestructura
fetch('../static/Archivos_exportados/infraestructura_nodos.geojson')
    .then(response => response.json())
    .then(data => {
        infraestructuraNodosLayer = L.geoJSON(data, {
            pointToLayer: function (feature, latlng) {
                return L.circleMarker(latlng, {
                    radius: 4,
                    fillColor: 'black',
                    color: 'black',
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.9
                });
            },
            onEachFeature: function (feature, layer) {
                if (feature.properties && feature.properties.id) {
                    layer.bindPopup("Nodo ID: " + feature.properties.id);
                }
            }
        })
        //.addTo(map);
    })
    .catch(error => console.error('Error cargando infraestructura_nodos.geojson:', error));

// Cargar y mostrar el archivo GeoJSON de Dijkstra
fetch('../static/dijkstra.geojson')
    .then(response => response.json())
    .then(data => {
        dijkstraLayer = L.geoJSON(null, {
            style: {
                color: '#FF4500',
                weight: 6,
                opacity: 0.9
            }
        })
        // .addTo(map);

        // Añadir las rutas al layer de Dijkstra
        L.geoJSON(data, {
            style: {
                color: '#FF4500',
                weight: 6,
                opacity: 0.9
            }
        }).addTo(dijkstraLayer);

        // Añadir los marcadores de inicio y meta al layer de Dijkstra
        L.geoJSON(data, {
            pointToLayer: function(feature, latlng) {
                if (feature.properties.role === "source") {
                    return L.marker(latlng, { icon: startIcon }).bindPopup("Inicio de la ruta");
                } else if (feature.properties.role === "target") {
                    return L.marker(latlng, { icon: endIcon }).bindPopup("Final de la ruta");
                }
            }
        }).addTo(dijkstraLayer);
    })
    .catch(error => console.error('Error cargando dijkstra.geojson:', error));

// Cargar y mostrar el archivo GeoJSON de estacionamientos
fetch('../static/Archivos_exportados/estacionamientos.geojson')
.then(response => response.json())
.then(data => {
    // Definir el ícono del SVG utilizando L.divIcon
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
        className: '', // O puedes definir una clase CSS si necesitas modificar el estilo
        iconSize: [24, 24],
        iconAnchor: [12, 12] // Centro del icono como el punto de anclaje
    });

    // Añadir los estacionamientos al mapa usando el ícono personalizado
    estacionamientosLayer = L.geoJSON(data, {
        pointToLayer: function (feature, latlng) {
            return L.marker(latlng, { icon: estacionamientoIcon });
        },
        onEachFeature: function (feature, layer) {
            if (feature.properties && feature.properties.name) {
                layer.bindPopup(feature.properties.name);
            }
        }
    });
    // No añadir al mapa por defecto, se activa cuando el usuario lo solicite
    // .addTo(map);
})
.catch(error => console.error('Error cargando estacionamientos.geojson:', error));


// Cargar y mostrar el archivo GeoJSON de velocidades máximas
fetch('../static/Archivos_exportados/velocidades_maximas.geojson')
    .then(response => response.json())
    .then(data => {
        velocidadesLayer = L.geoJSON(data, {
            style: function (feature) {
                var maxspeed = feature.properties.maxspeed;
                var color;

                if (maxspeed === "50") {
                    color = 'red';
                } else if (maxspeed === "40") {
                    color = 'blue';
                } else {
                    color = 'gray';
                }

                return {
                    color: color,
                    weight: 4,
                    opacity: 0.9
                };
            }
        })
        // .addTo(map);
    })
    .catch(error => console.error('Error cargando velocidades_maximas.geojson:', error));

// Función para definir el color basado en el índice de riesgo de precipitación
function getColorPrecipitation(value) {
    return value === null ? 'gray' : // Sin datos
            value > 10   ? '#00008b' : // Azul oscuro (mayor precipitación)
            value > 5    ? '#4169e1' : // Azul medio
            value >= 0   ? '#add8e6' : // Azul claro (incluso para 0.0)
                            'gray';    // Valor no válido
}

// Variable para almacenar los datos de precipitaciones
var precipitacionesData = {};

// Cargar los datos de precipitaciones
fetch('../static/Archivos_exportados/precipitacion_comunas_rm.json')
    .then(response => response.json())
    .then(data => {
        data.forEach(function(entry) {
            precipitacionesData[entry.comuna] = parseFloat(entry.precip_mm); // Guardamos las precipitaciones por comuna
        });
    })
    .catch(error => console.error('Error cargando precipitacion_comunas_rm.json:', error));

// Cargar y mostrar el archivo GeoJSON de inundaciones
fetch('../static/Archivos_exportados/inundaciones.geojson')
    .then(response => response.json())
    .then(data => {
        var inundacionesLayer = L.geoJSON(data, {
            style: function(feature) {
                var comuna = feature.properties.nom_comuna;
                var precipValue = precipitacionesData[comuna]; // Buscamos si la comuna tiene datos de precipitación
                return {
                    fillColor: getColorPrecipitation(precipValue), // Usamos el valor de precipitación si existe
                    weight: 2,
                    opacity: 1,
                    color: 'black',
                    fillOpacity: 0.7
                };
            },
            onEachFeature: function(feature, layer) {
                var comuna = feature.properties.nom_comuna;
                var precipValue = precipitacionesData[comuna] !== undefined ? precipitacionesData[comuna] : 'Sin datos';
                var popupContent = "<strong>Comuna:</strong> " + comuna + "<br>" +
                                    "<strong>Precipitación:</strong> " + precipValue + " mm";
                layer.bindPopup(popupContent);
            }
        })
        // .addTo(map);

        // Toggle de la capa de precipitaciones
        document.getElementById('toggle-precipitacion').addEventListener('click', function() {
            if (map.hasLayer(inundacionesLayer)) {
                map.removeLayer(inundacionesLayer);
            } else {
                map.addLayer(inundacionesLayer);
            }
        });
    })
    .catch(error => console.error('Error cargando inundaciones.geojson:', error));

// Función para definir el color basado en el índice de riesgo
function getColor(d) {
    return d === null ? 'gray' :
            d > 0.05  ? '#FF0000' : // Rojo para valores altos
            d > 0.03  ? '#FF8C00' : // Naranja
            d > 0.01  ? '#FFD700' : // Amarillo
            d > 0     ? '#9ACD32' : // Verde claro
                        '#00FF00';  // Verde
}

// Cargar y mostrar el archivo GeoJSON de inundaciones
fetch('../static/Archivos_exportados/inundaciones.geojson')
    .then(response => response.json())
    .then(data => {
        var inundacionesLayer = L.geoJSON(data, {
            style: function(feature) {
                var riesgo = feature.properties.ind_riesgo_inundaciones_t10_delta;
                return {
                    fillColor: getColor(riesgo),
                    weight: 2,
                    opacity: 1,
                    color: 'black',
                    fillOpacity: 0.7
                };
            },
            onEachFeature: function(feature, layer) {
                var popupContent = "<strong>Comuna:</strong> " + feature.properties.nom_comuna + "<br>" +
                                    "<strong>Riesgo de Inundación:</strong> " + (feature.properties.ind_riesgo_inundaciones_t10_delta !== null ? feature.properties.ind_riesgo_inundaciones_t10_delta : 'Sin datos');
                layer.bindPopup(popupContent);
            }
        })
        // .addTo(map);

        // Toggle de la capa de inundaciones
        document.getElementById('toggle-inundaciones').addEventListener('click', function() {
            if (map.hasLayer(inundacionesLayer)) {
                map.removeLayer(inundacionesLayer);
            } else {
                map.addLayer(inundacionesLayer);
            }
        });
    })
    .catch(error => console.error('Error cargando inundaciones.geojson:', error));

// Función para definir el color basado en el índice de seguridad
function getColorSeguridad(value) {
    return value === null ? 'gray' :
            value >= 900 ? '#FF0000' : // Crítico
            value >= 660 ? '#FF8C00' : // Alto
            value >= 350 ? '#FFD700' : // Medio
                            '#00FF00';  // Bajo
}

// Cargar y mostrar la capa de seguridad desde el archivo JSON
fetch('../static/Archivos_exportados/seguridad_comunas_rm.json')
    .then(response => response.json())
    .then(data => {
        seguridadLayer = L.geoJSON(null, {
            style: function(feature) {
                var comuna = feature.properties.nom_comuna;
                var value = parseFloat(data[comuna]); // Obtener el valor de seguridad de la comuna del archivo JSON
                return {
                    fillColor: getColorSeguridad(value),
                    weight: 2,
                    opacity: 1,
                    color: 'black',
                    fillOpacity: 0.7
                };
            },
            onEachFeature: function(feature, layer) {
                var comuna = feature.properties.nom_comuna;
                var value = data[comuna] !== undefined ? data[comuna] : 'Sin datos';
                var popupContent = "<strong>Comuna:</strong> " + comuna + "<br>" +
                                    "<strong>Índice de Seguridad:</strong> " + value;
                layer.bindPopup(popupContent);
            }
        });

        // Cargar y mostrar el archivo GeoJSON de inundaciones para asociar las comunas
        fetch('../static/Archivos_exportados/inundaciones.geojson')
            .then(response => response.json())
            .then(dataInundaciones => {
                L.geoJSON(dataInundaciones, {
                    style: function(feature) {
                        var comuna = feature.properties.nom_comuna;
                        var value = parseFloat(data[comuna]); // Obtener el valor de seguridad del archivo JSON
                        return {
                            fillColor: getColorSeguridad(value),
                            weight: 2,
                            opacity: 1,
                            color: 'black',
                            fillOpacity: 0.7
                        };
                    },
                    onEachFeature: function(feature, layer) {
                        var comuna = feature.properties.nom_comuna;
                        var value = data[comuna] !== undefined ? data[comuna] : 'Sin datos';
                        var popupContent = "<strong>Comuna:</strong> " + comuna + "<br>" +
                                            "<strong>Índice de Seguridad:</strong> " + value;
                        layer.bindPopup(popupContent);
                    }
                }).addTo(seguridadLayer);
            })
            .catch(error => console.error('Error cargando inundaciones.geojson:', error));

        // seguridadLayer.addTo(map);

        // Toggle de la capa de seguridad
        document.getElementById('toggle-seguridad').addEventListener('click', function() {
            if (map.hasLayer(seguridadLayer)) {
                map.removeLayer(seguridadLayer);
            } else {
                map.addLayer(seguridadLayer);
            }
        });
    })
    .catch(error => console.error('Error cargando seguridad_comunas_rm.json:', error));

// Función para definir el color basado en el estado de cierre de calles
function getColorCierre(roadClosure) {
    return roadClosure === "Yes" ? '#FF0000' :
            roadClosure === "No" ? '#00FF00' :
                                    'gray';
}

// Cargar y mostrar la capa de cierre de calles desde el archivo JSON
fetch('../static/Archivos_exportados/cierres_calles.json')
    .then(response => response.json())
    .then(data => {
        cierreCallesLayer = L.geoJSON(null, {
            style: function(feature) {
                var streetName = feature.properties.name;
                var roadClosureData = data.find(street => street.name === streetName);
                var roadClosure = roadClosureData ? roadClosureData.road_closure : 'Sin datos';
                return {
                    fillColor: getColorCierre(roadClosure),
                    weight: 2,
                    opacity: 1,
                    color: getColorCierre(roadClosure),
                    fillOpacity: 0.7
                };
            },
            onEachFeature: function(feature, layer) {
                var streetName = feature.properties.name;
                var roadClosureData = data.find(street => street.name === streetName);
                var roadClosure = roadClosureData ? roadClosureData.road_closure : 'Sin datos';
                var popupContent = "<strong>Calle:</strong> " + streetName + "<br>" +
                                    "<strong>Cierre de Calle:</strong> " + roadClosure;
                layer.bindPopup(popupContent);
            }
        });

        // Cargar y mostrar el archivo GeoJSON de infraestructura para asociar las calles
        fetch('../static/Archivos_exportados/infraestructura.geojson')
            .then(response => response.json())
            .then(dataInfraestructura => {
                L.geoJSON(dataInfraestructura, {
                    style: function(feature) {
                        var streetName = feature.properties.name;
                        var roadClosureData = data.find(street => street.name === streetName);
                        var roadClosure = roadClosureData ? roadClosureData.road_closure : 'Sin datos';
                        return {
                            fillColor: getColorCierre(roadClosure),
                            weight: 2,
                            opacity: 1,
                            color: getColorCierre(roadClosure),
                            fillOpacity: 0.7
                        };
                    },
                    onEachFeature: function(feature, layer) {
                        var streetName = feature.properties.name;
                        var roadClosureData = data.find(street => street.name === streetName);
                        var roadClosure = roadClosureData ? roadClosureData.road_closure : 'Sin datos';
                        var popupContent = "<strong>Calle:</strong> " + streetName + "<br>" +
                                            "<strong>Cierre de Calle:</strong> " + roadClosure;
                        layer.bindPopup(popupContent);
                    }
                }).addTo(cierreCallesLayer);
            })
            .catch(error => console.error('Error cargando infraestructura.geojson:', error));

        // cierreCallesLayer.addTo(map);

        // Toggle de la capa de cierre de calles
        document.getElementById('toggle-cierres').addEventListener('click', function() {
            if (map.hasLayer(cierreCallesLayer)) {
                map.removeLayer(cierreCallesLayer);
            } else {
                map.addLayer(cierreCallesLayer);
            }
        });
    })
    .catch(error => console.error('Error cargando cierres_calles.json:', error));


// Función para definir el color basado en el nivel de congestión
function getTrafficColor(speed) {
    return speed <= 20 ? '#FF0000' : // Muy alta congestión
            speed <= 30 ? '#FFA500' : // Alta congestión
            speed <= 40 ? '#FFFF00' : // Tráfico moderado
                            '#00FF00';  // Sin congestión
}
    
// Cargar y mostrar la capa de tráfico actual desde el archivo JSON
fetch('../static/Archivos_exportados/trafico_actual.json')
    .then(response => response.json())
    .then(data => {
        traficoLayer = L.geoJSON(null, {
            style: function(feature) {
                var streetName = feature.properties.name;
                var trafficData = data.find(street => street.name === streetName);
                var speed = trafficData ? trafficData.current_speed : null;
                return {
                    color: speed !== null ? getTrafficColor(speed) : 'gray',
                    weight: 3,
                    opacity: 0.8
                };
            },
            onEachFeature: function(feature, layer) {
                var streetName = feature.properties.name;
                var trafficData = data.find(street => street.name === streetName);
                var speed = trafficData ? trafficData.current_speed : 'Sin datos';
                var popupContent = "<strong>Calle:</strong> " + streetName + "<br>" +
                                    "<strong>Velocidad Actual:</strong> " + speed + " km/h";
                layer.bindPopup(popupContent);
            }
        });
    
// Cargar y mostrar el archivo GeoJSON de infraestructura para asociar las calles
fetch('../static/Archivos_exportados/infraestructura.geojson')
    .then(response => response.json())
    .then(dataInfraestructura => {
        L.geoJSON(dataInfraestructura, {
            style: function(feature) {
                var streetName = feature.properties.name;
                var trafficData = data.find(street => street.name === streetName);
                var speed = trafficData ? trafficData.current_speed : null;
                return {
                    color: speed !== null ? getTrafficColor(speed) : 'gray',
                    weight: 3,
                    opacity: 0.8
                };
            },
            onEachFeature: function(feature, layer) {
                var streetName = feature.properties.name;
                var trafficData = data.find(street => street.name === streetName);
                var speed = trafficData ? trafficData.current_speed : 'Sin datos';
                var popupContent = "<strong>Calle:</strong> " + streetName + "<br>" +
                                            "<strong>Velocidad Actual:</strong> " + speed + " km/h";
                layer.bindPopup(popupContent);
            }
        }).addTo(traficoLayer);
    })
    .catch(error => console.error('Error cargando infraestructura.geojson:', error));
    
    // traficoLayer.addTo(map);
    
    // Toggle de la capa de tráfico
    document.getElementById('toggle-trafico').addEventListener('click', function() {
        if (map.hasLayer(traficoLayer)) {
            map.removeLayer(traficoLayer);
        } else {
            map.addLayer(traficoLayer);
        }
    });
})
.catch(error => console.error('Error cargando trafico_actual.json:', error));


document.getElementById('toggle-simbologia-btn').addEventListener('click', function() {
    var simbologia = document.getElementById('simbologia');
    if (simbologia.style.display === 'none' || !simbologia.style.display) {
        simbologia.style.display = 'block';
    } else {
        simbologia.style.display = 'none';
    }
});


    
// Funciones para alternar la visibilidad de las capas
function toggleLayer(layer) {
    if (map.hasLayer(layer)) {
        map.removeLayer(layer);
    } else {
        map.addLayer(layer);
    }
}

// Asignar eventos de clic a la simbología
document.getElementById('toggle-infraestructura').addEventListener('click', function() {
    toggleLayer(infraestructuraLayer);
});

document.getElementById('toggle-infraestructura-nodos').addEventListener('click', function() {
    toggleLayer(infraestructuraNodosLayer);
});

document.getElementById('toggle-dijkstra').addEventListener('click', function() {
    toggleLayer(dijkstraLayer);
});

document.getElementById('toggle-estacionamientos').addEventListener('click', function() {
    toggleLayer(estacionamientosLayer);
});

document.getElementById('toggle-velocidades').addEventListener('click', function() {
    toggleLayer(velocidadesLayer);
});
