import requests
import geojson
from geojson import FeatureCollection, Feature, LineString
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

overpass_query = """
[out:json][timeout:25];
(
  way["highway"="primary"]({bbox});
  way["highway"="secondary"]({bbox});
);
out body;
>;
out skel qt;
"""

overpass_query = overpass_query.format(bbox=bbox)

overpass_url = "http://overpass-api.de/api/interpreter"
response = requests.get(overpass_url, params={'data': overpass_query})

if response.status_code == 200:
    data = response.json()
    elements = data['elements']
    features = []

    nodes = {elem['id']: elem for elem in elements if elem['type'] == 'node'}

    for elem in elements:
        if elem['type'] == 'way':
            coords = []
            for node_id in elem['nodes']:
                node = nodes.get(node_id)
                if node:
                    coords.append((node['lon'], node['lat']))
            if coords:
                geometry = LineString(coords)
                desired_properties = ['highway', 'lanes', 'name', 'oneway']
                tags = elem.get('tags', {})
                properties = {key: tags.get(key) for key in desired_properties if key in tags}
                properties['id'] = elem['id']
                feature = Feature(geometry=geometry, properties=properties)
                features.append(feature)

    feature_collection = FeatureCollection(features)

    with open('./Archivos_descargados/calles_primarias_secundarias_santiago.geojson', 'w', encoding='utf-8') as f:
        geojson.dump(feature_collection, f, ensure_ascii=False, indent=4)
    print("GeoJSON guardado exitosamente.")
else:
    print(f"Error al obtener datos: {response.status_code}")
    print(response.text)
