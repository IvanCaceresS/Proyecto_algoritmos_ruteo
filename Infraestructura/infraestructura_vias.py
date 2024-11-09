import requests
import geojson
from geojson import FeatureCollection, Feature, LineString
from dotenv import load_dotenv
import os
from shapely.geometry import shape, LineString as ShapelyLineString, Polygon
import json

# Cargar variables de entorno
load_dotenv('../.env')

# Configuración del BBOX
BBOX_RM = os.getenv("BBOX_RM")
BBOX_ZONA_PEQUENA = os.getenv("BBOX_ZONA_PEQUENA")
USAR_BBOX_RM = os.getenv("USAR_BBOX_RM")

bbox_values = BBOX_RM.split(',') if USAR_BBOX_RM == "True" else BBOX_ZONA_PEQUENA.split(',')
norte, sur, este, oeste = bbox_values
bbox = f"{sur},{oeste},{norte},{este}"

# URL de descarga de 13.geojson
url = "https://raw.githubusercontent.com/caracena/chile-geojson/refs/heads/master/13.geojson"

# Lista de comunas a conservar
# comunas_deseadas = [
#     "Alhué", "Buin", "Calera de Tango", "Cerrillos", "Cerro Navia", "Colina", 
#     "Conchalí", "Curacaví", "El Bosque", "El Monte", "Estación Central", 
#     "Huechuraba", "Independencia", "Isla de Maipo", "La Cisterna", "La Florida", 
#     "La Granja", "La Pintana", "La Reina", "Lampa", "Las Condes", "Lo Barnechea", 
#     "Lo Espejo", "Lo Prado", "Macul", "Maipú", "María Pinto", "Melipilla", 
#     "Padre Hurtado", "Paine", "Pedro Aguirre Cerda", "Peñaflor", "Peñalolén", 
#     "Pirque", "Providencia", "Pudahuel", "Puente Alto", "Quilicura", 
#     "Quinta Normal", "Recoleta", "Renca", "San Bernardo", "San Joaquín", 
#     "San José de Maipo", "San Miguel", "San Pedro", "San Ramón", "Santiago", 
#     "Talagante", "Tiltil", "Vitacura", "Ñuñoa"
# ]

comunas_deseadas = ["La Cisterna"]

#Eliminar archivo si existe
try:
    os.remove('./Archivos_descargados/13.geojson')
except FileNotFoundError:
    pass

# Descargar el archivo geojson
try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    print(f"Error al descargar el archivo: {e}")
    exit(1)

# Filtrar las comunas deseadas
filtered_features = [
    feature for feature in data['features']
    if feature.get('properties', {}).get('Comuna') in comunas_deseadas
]

# Sobrescribir 13.geojson con las comunas deseadas
filtered_data = {
    'type': 'FeatureCollection',
    'features': filtered_features
}

output_filename = './Archivos_descargados/13.geojson'
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(filtered_data, f, ensure_ascii=False, indent=4)
    print(f"Archivo GeoJSON filtrado guardado y sobrescrito como '{output_filename}'.")

# Cargar polígonos desde 13.geojson
with open('./Archivos_descargados/13.geojson', 'r', encoding='utf-8') as f:
    region_data = geojson.load(f)
    region_polygons = [shape(feature["geometry"]) for feature in region_data["features"] if feature["geometry"]["type"] == "Polygon"]

# Consulta a Overpass API muchas calles
overpass_query = f"""
[out:json][timeout:25];
(
  way["highway"]({bbox});
);
out body;
>;
out skel qt;
"""
# overpass_query = f"""
# [out:json][timeout:25];
# (
#   way["highway"="primary"]({bbox});
#   way["highway"="secondary"]({bbox});
#   way["highway"="tertiary"]({bbox});
#   way["highway"="residential"]({bbox});
# );
# out body;
# >;
# out skel qt;
# """
# Consulta a Overpass API pocas calles
# overpass_query = f"""
# [out:json][timeout:25];
# (
#     way["highway"="primary"]({bbox});
#     way["highway"="secondary"]({bbox});
# );
# out body;
# >;
# out skel qt;
# """

overpass_url = "http://overpass-api.de/api/interpreter"
response = requests.get(overpass_url, params={'data': overpass_query})

if response.status_code == 200:
    data = response.json()
    elements = data['elements']
    features = []

    nodes = {elem['id']: elem for elem in elements if elem['type'] == 'node'}

    # Procesar cada elemento y verificar si está contenido en los polígonos
    for elem in elements:
        if elem['type'] == 'way':
            coords = [(nodes[node_id]['lon'], nodes[node_id]['lat']) for node_id in elem['nodes'] if node_id in nodes]
            if coords:
                # Convertir las coordenadas de la calle a un objeto Shapely LineString
                line = ShapelyLineString(coords)

                # Verificar si la línea está contenida en algún polígono de la región
                if any(polygon.contains(line) for polygon in region_polygons):
                    geometry = LineString(coords)
                    desired_properties = ['highway', 'lanes', 'name', 'oneway']
                    tags = elem.get('tags', {})
                    properties = {key: tags.get(key) for key in desired_properties if key in tags}
                    properties['id'] = elem['id']
                    feature = Feature(geometry=geometry, properties=properties)
                    features.append(feature)

    # Crear y guardar el FeatureCollection filtrado
    feature_collection = FeatureCollection(features)

    with open('./Archivos_descargados/calles_primarias_secundarias_santiago.geojson', 'w', encoding='utf-8') as f:
        geojson.dump(feature_collection, f, ensure_ascii=False, indent=4)
    print("GeoJSON guardado exitosamente con las calles contenidas en los polígonos.")
else:
    print(f"Error al obtener datos: {response.status_code}")
    print(response.text)
