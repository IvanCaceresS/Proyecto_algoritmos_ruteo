import requests
import geojson
from geojson import FeatureCollection, Feature, Point, LineString, Polygon

# Definir las coordenadas del bounding box
norte = -33.2467   # Latitud máxima
sur = -33.8454     # Latitud mínima
este = -70.4333    # Longitud máxima
oeste = -70.9360   # Longitud mínima

# Crear la variable del bounding box en el orden: sur, oeste, norte, este
bbox = f"{sur},{oeste},{norte},{este}"

# Definir la consulta de Overpass
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
