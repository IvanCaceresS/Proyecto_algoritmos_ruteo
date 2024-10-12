import requests
import geojson
from geojson import FeatureCollection, Feature, LineString

# Definir las coordenadas del bounding box
norte = -33.2467   # Latitud máxima
sur = -33.8454     # Latitud mínima
este = -70.4333    # Longitud máxima
oeste = -70.9360   # Longitud mínima

# Crear la variable del bounding box en el orden: sur, oeste, norte, este
bbox = f"{sur},{oeste},{norte},{este}"

# Definir la consulta de Overpass
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

# Reemplazar {bbox} en la consulta con las coordenadas del bounding box
overpass_query = overpass_query.format(bbox=bbox)

# Enviar la solicitud a Overpass API
overpass_url = "http://overpass-api.de/api/interpreter"
response = requests.get(overpass_url, params={'data': overpass_query})

# Verificar la respuesta y procesar el GeoJSON
if response.status_code == 200:
    data = response.json()
    elements = data['elements']
    features = []

    # Crear un diccionario para los nodos
    nodes = {elem['id']: elem for elem in elements if elem['type'] == 'node'}

    # Procesar las vías
    for elem in elements:
        if elem['type'] == 'way':
            coords = []
            for node_id in elem['nodes']:
                node = nodes.get(node_id)
                if node:
                    coords.append((node['lon'], node['lat']))
            if coords:
                geometry = LineString(coords)
                # Filtrar las propiedades deseadas
                desired_properties = ['highway', 'lanes', 'name']
                tags = elem.get('tags', {})
                properties = {key: tags.get(key) for key in desired_properties if key in tags}
                properties['id'] = elem['id']
                feature = Feature(geometry=geometry, properties=properties)
                features.append(feature)

    feature_collection = FeatureCollection(features)

    # Guardar el resultado en un archivo GeoJSON
    with open('./Archivos_descargados/calles_primarias_secundarias_santiago.geojson', 'w', encoding='utf-8') as f:
        geojson.dump(feature_collection, f, ensure_ascii=False, indent=4)
    print("GeoJSON guardado exitosamente.")
else:
    print(f"Error al obtener datos: {response.status_code}")
    print(response.text)
