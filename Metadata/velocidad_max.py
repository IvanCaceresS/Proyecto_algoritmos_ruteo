import requests
import geojson
from geojson import FeatureCollection, Feature, LineString
from dotenv import load_dotenv
import os
from shapely.geometry import shape, LineString as ShapelyLineString, Polygon

# Cargar variables de entorno
load_dotenv('../.env')

# Configuración del BBOX
BBOX_RM = os.getenv("BBOX_RM")
BBOX_ZONA_PEQUENA = os.getenv("BBOX_ZONA_PEQUENA")
USAR_BBOX_RM = os.getenv("USAR_BBOX_RM")

bbox_values = BBOX_RM.split(',') if USAR_BBOX_RM == "True" else BBOX_ZONA_PEQUENA.split(',')
norte, sur, este, oeste = bbox_values
bbox = f"{sur},{oeste},{norte},{este}"

# Cargar los polígonos de 13.geojson
with open('../Infraestructura/Archivos_descargados/13.geojson', 'r', encoding='utf-8') as f:
    region_data = geojson.load(f)
    region_polygons = [shape(feature["geometry"]) for feature in region_data["features"] if feature["geometry"]["type"] == "Polygon"]

# Consulta a Overpass API para obtener datos de carreteras con límites de velocidad
overpass_query = f"""
[out:json][timeout:25];
(
  way["highway"="primary"]({bbox});
  way["highway"="secondary"]({bbox});
);
out body;
>;
out skel qt;
"""

overpass_url = "https://overpass-api.de/api/interpreter"
response = requests.get(overpass_url, params={'data': overpass_query})

if response.status_code == 200:
    data = response.json()
    elements = data['elements']
    features = []

    nodes = {elem['id']: elem for elem in elements if elem['type'] == 'node'}

    # Procesar cada elemento y verificar si está contenido en los polígonos
    for elem in elements:
        if elem['type'] == 'way':
            way_id = elem['id']
            tags = elem.get('tags', {})
            maxspeed = tags.get('maxspeed')
            coords = [(nodes[node_id]['lon'], nodes[node_id]['lat']) for node_id in elem['nodes'] if node_id in nodes]
            if coords:
                # Convertir las coordenadas de la carretera a un objeto Shapely LineString
                line = ShapelyLineString(coords)

                # Verificar si la línea está contenida en algún polígono de la región
                if any(polygon.contains(line) for polygon in region_polygons):
                    geometry = LineString(coords)
                    properties = {
                        'id': way_id,
                        'maxspeed': maxspeed
                    }
                    feature = Feature(geometry=geometry, properties=properties)
                    features.append(feature)

    # Crear y guardar el FeatureCollection filtrado
    feature_collection = FeatureCollection(features)

    with open('./Archivos_descargados/velocidades_maximas.geojson', 'w', encoding='utf-8') as f:
        geojson.dump(feature_collection, f, ensure_ascii=False, indent=4)
    print("Archivo GeoJSON guardado exitosamente con las carreteras contenidas en los polígonos.")
else:
    print(f"Error al obtener datos: {response.status_code}")
    print(response.text)
