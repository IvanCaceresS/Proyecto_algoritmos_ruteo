import requests
import geojson
from geojson import FeatureCollection, Feature, Point, LineString, Polygon
from dotenv import load_dotenv
import os

load_dotenv('../.env')

BBOX_RM = os.getenv("BBOX_RM")
BBOX_ZONA_PEQUENA = os.getenv("BBOX_ZONA_PEQUENA")
USAR_BBOX_RM = os.getenv("USAR_BBOX_RM")

if USAR_BBOX_RM == "True":
    bbox_values = BBOX_RM.split(',')
else:
    bbox_values = BBOX_ZONA_PEQUENA.split(',')

norte = bbox_values[0]
sur = bbox_values[1]
este = bbox_values[2]
oeste = bbox_values[3]

bbox = f"{sur},{oeste},{norte},{este}"

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

    nodes = {}
    ways = {}
    relations = {}

    for elem in elements:
        if elem['type'] == 'node':
            nodes[elem['id']] = elem

    for elem in elements:
        if elem['type'] == 'way':
            ways[elem['id']] = elem

    for elem in elements:
        if elem['type'] == 'node' and 'tags' in elem:
            lon = elem['lon']
            lat = elem['lat']
            geometry = Point((lon, lat))
            properties = elem.get('tags', {})
            feature = Feature(geometry=geometry, properties=properties, id=f"node/{elem['id']}")
            features.append(feature)
        elif elem['type'] == 'way' and 'tags' in elem:
            coords = []
            for node_id in elem['nodes']:
                node = nodes.get(node_id)
                if node:
                    coords.append((node['lon'], node['lat']))
            if coords:
                if coords[0] == coords[-1]:
                    geometry = Polygon([coords])
                else:
                    geometry = LineString(coords)
                properties = elem.get('tags', {})
                feature = Feature(geometry=geometry, properties=properties, id=f"way/{elem['id']}")
                features.append(feature)
        elif elem['type'] == 'relation' and 'tags' in elem:
            pass

    feature_collection = FeatureCollection(features)

    with open('./Archivos_descargados/estacionamientos.geojson', 'w', encoding='utf-8') as f:
        geojson.dump(feature_collection, f, ensure_ascii=False, indent=4)
    print("Archivo GeoJSON guardado exitosamente.")
else:
    print(f"Error al obtener datos: {response.status_code}")
    print(response.text)
