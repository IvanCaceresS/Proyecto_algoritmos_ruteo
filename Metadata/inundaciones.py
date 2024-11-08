import requests
import json
from shapely.geometry import shape
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv('../.env')

# Extraer las comunas de 13.geojson en mayúsculas
def obtener_comunas_desde_geojson(archivo_geojson):
    with open(archivo_geojson, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    comunas = set()
    for feature in data['features']:
        properties = feature.get('properties', {})
        comuna = properties.get('Comuna', None)
        if comuna:
            comunas.add(comuna.upper())  # Convertir a mayúsculas
    return comunas

# Obtener las comunas de 13.geojson
archivo_geojson = '../Infraestructura/Archivos_descargados/13.geojson'
comunas_de_13 = obtener_comunas_desde_geojson(archivo_geojson)

# URL de descarga
url = "https://arclim.mma.gob.cl/features/attributes/comunas/?attributes=NOM_COMUNA,NOM_PROVIN,NOM_REGION,ind_riesgo_inundaciones_t10_delta&format=geojson&file_name=ARCLIM_inundaciones_urbanas_comunas"

# Descargar y filtrar datos
try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    print(f"Error al descargar el archivo: {e}")
    exit(1)

# Filtrar características
filtered_features = []
desired_properties = [
    "NOM_REGION",
    "NOM_COMUNA",
    "NOM_PROVIN",
    "ind_riesgo_inundaciones_t10_delta"
]

for feature in data['features']:
    properties = feature['properties']
    comuna = properties.get('NOM_COMUNA', '').upper()  # Convertir comuna a mayúsculas para comparación
    if properties.get('NOM_REGION') == 'REGIÓN METROPOLITANA DE SANTIAGO' and comuna in comunas_de_13:
        # Crear un nuevo conjunto de propiedades filtradas
        new_properties = {key: properties.get(key) for key in desired_properties}
        new_feature = {
            'type': 'Feature',
            'geometry': feature['geometry'],
            'properties': new_properties
        }
        filtered_features.append(new_feature)

# Guardar el archivo filtrado
filtered_data = {
    'type': 'FeatureCollection',
    'features': filtered_features
}

output_filename = './Archivos_descargados/inundaciones.geojson'
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(filtered_data, f, ensure_ascii=False, indent=4)
    print(f"Archivo GeoJSON filtrado guardado como '{output_filename}'.")
