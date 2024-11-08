import requests
import geojson
from geojson import FeatureCollection, Feature, Point, LineString, Polygon
from dotenv import load_dotenv
import os
from shapely.geometry import shape, Point as ShapelyPoint, LineString as ShapelyLineString, Polygon as ShapelyPolygon

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

# Consulta a Overpass API para obtener estacionamientos de bicicletas
overpass_query = f"""
[out:json][timeout:25];
(
  nwr["amenity"="bicycle_parking"]({bbox});
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
        if elem['type'] == 'node' and 'tags' in elem:
            # Crear el punto y verificar si está contenido en algún polígono
            point = ShapelyPoint(elem['lon'], elem['lat'])
            if any(polygon.contains(point) for polygon in region_polygons):
                geometry = Point((elem['lon'], elem['lat']))
                properties = elem.get('tags', {})
                feature = Feature(geometry=geometry, properties=properties, id=f"node/{elem['id']}")
                features.append(feature)

        elif elem['type'] == 'way' and 'tags' in elem:
            # Crear LineString o Polygon según las coordenadas y verificar si está contenido
            coords = [(nodes[node_id]['lon'], nodes[node_id]['lat']) for node_id in elem['nodes'] if node_id in nodes]
            if coords:
                if coords[0] == coords[-1]:  # Es un polígono cerrado
                    line_or_polygon = ShapelyPolygon(coords)
                    geometry = Polygon([coords])
                else:  # Es una línea abierta
                    line_or_polygon = ShapelyLineString(coords)
                    geometry = LineString(coords)
                
                # Solo añadir si está contenido en algún polígono
                if any(polygon.contains(line_or_polygon) for polygon in region_polygons):
                    properties = elem.get('tags', {})
                    feature = Feature(geometry=geometry, properties=properties, id=f"way/{elem['id']}")
                    features.append(feature)

    # Crear y guardar el FeatureCollection filtrado
    feature_collection = FeatureCollection(features)

    with open('./Archivos_descargados/estacionamientos.geojson', 'w', encoding='utf-8') as f:
        geojson.dump(feature_collection, f, ensure_ascii=False, indent=4)
    print("Archivo GeoJSON guardado exitosamente con los estacionamientos dentro de los polígonos.")
else:
    print(f"Error al obtener datos: {response.status_code}")
    print(response.text)
