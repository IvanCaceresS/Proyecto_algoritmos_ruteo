import os
import requests
import geojson
from geojson import Feature, FeatureCollection, LineString
from dotenv import load_dotenv
from shapely.geometry import shape, LineString as ShapelyLineString
import json

load_dotenv('../.env')

def obtener_bbox():
    BBOX_RM = os.getenv("BBOX_RM")
    BBOX_ZONA_PEQUENA = os.getenv("BBOX_ZONA_PEQUENA")
    USAR_BBOX_RM = os.getenv("USAR_BBOX_RM")

    bbox_values = BBOX_RM.split(',') if USAR_BBOX_RM == "True" else BBOX_ZONA_PEQUENA.split(',')
    norte, sur, este, oeste = bbox_values
    return f"{sur},{oeste},{norte},{este}"

def descargar_archivo_geojson(url, output_path):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el archivo: {e}")
        return None

def filtrar_comunas(data, comunas_deseadas):
    return [
        feature for feature in data['features']
        if feature.get('properties', {}).get('Comuna') in comunas_deseadas
    ]

def cargar_poligonos(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        region_data = geojson.load(f)
        return [shape(feature["geometry"]) for feature in region_data["features"] if feature["geometry"]["type"] == "Polygon"]

def obtener_calles_overpass(bbox, region_polygons):

    # Consulta a Overpass API muchas calles
    # overpass_query = f"""
    # [out:json][timeout:25];
    # (
    #   way["highway"]({bbox});
    # );
    # out body;
    # >;
    # out skel qt;
    # """

    overpass_query = f"""
    [out:json][timeout:25];
    (
      way["highway"="primary"]({bbox});
      way["highway"="secondary"]({bbox});
      way["highway"="tertiary"]({bbox});
      way["highway"="residential"]({bbox});
    );
    out body;
    >;
    out skel qt;
    """

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
    features = []

    if response.status_code == 200:
        data = response.json()
        elements = data['elements']
        nodes = {elem['id']: elem for elem in elements if elem['type'] == 'node'}

        for elem in elements:
            if elem['type'] == 'way':
                coords = [(nodes[node_id]['lon'], nodes[node_id]['lat']) for node_id in elem['nodes'] if node_id in nodes]
                if coords:
                    line = ShapelyLineString(coords)
                    if any(polygon.intersects(line) for polygon in region_polygons):
                        geometry = LineString(coords)
                        desired_properties = ['highway', 'lanes', 'name', 'oneway']
                        properties = {key: elem.get('tags', {}).get(key) for key in desired_properties if key in elem.get('tags', {})}
                        properties['id'] = elem['id']
                        features.append(Feature(geometry=geometry, properties=properties))
        return FeatureCollection(features)
    else:
        print(f"Error al obtener datos: {response.status_code}")
        return None

def guardar_geojson(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        geojson.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Archivo guardado como '{filename}'")

url = "https://raw.githubusercontent.com/caracena/chile-geojson/refs/heads/master/13.geojson"
output_geojson_path = './Archivos_descargados/13.geojson'
filtered_output_path = './Archivos_descargados/calles_primarias_secundarias_santiago.geojson'
bbox = obtener_bbox()

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

comunas_deseadas = ["Santiago"]

# Comunas noreste
#comunas_deseadas = ["Lo Barnechea", "Vitacura", "Las Condes", "Providencia", "Ñuñoa", "La Reina"]

# Comunas noroeste
#comunas_deseadas = ["Huechuraba", "Conchalí", "Quilicura", "Recoleta", "Independencia", "Renca", "Cerro Navia", "Quinta Normal", "Santiago", "Pudahuel", "Lo Prado", "Estación Central"]

# Comunas suroeste
#comunas_deseadas = ["Padre Hurtado", "Maipu", "Cerrillos", "Pedro Aguirre Cerda", "San Miguel", "Lo Espejo", "La Cisterna", "El Bosque", "San Bernardo"]

# Comunas sureste
#comunas_deseadas = ["San Joaquín", "Macul", "La Florida", "La Granja", "La Pintana", "Peñalolén", "San Ramón", "Puente Alto", "San José de Maipo", "Pirque"]

# Proceso principal
# Descargar y filtrar archivo GeoJSON de comunas
data = descargar_archivo_geojson(url, output_geojson_path)
if data:
    filtered_features = filtrar_comunas(data, comunas_deseadas)
    filtered_data = {'type': 'FeatureCollection', 'features': filtered_features}
    guardar_geojson(filtered_data, output_geojson_path)
    region_polygons = cargar_poligonos(output_geojson_path)
    feature_collection = obtener_calles_overpass(bbox, region_polygons)
    if feature_collection:
        guardar_geojson(feature_collection, filtered_output_path)