import requests
import time
import json
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv(dotenv_path='../.env')

api_key = os.getenv("WEATHER_API_KEY")

# Función para leer las comunas desde el archivo inundaciones.geojson
def obtener_comunas_desde_geojson(archivo_geojson):
    with open(archivo_geojson, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extraer los nombres de las comunas desde el campo "NOM_COMUNA"
    comunas = set()  # Usar un set para evitar duplicados
    for feature in data['features']:
        properties = feature.get('properties', {})
        comuna = properties.get('NOM_COMUNA', None)
        if comuna:
            comunas.add(comuna)
    
    return list(comunas)

# Obtener comunas desde el archivo GeoJSON
archivo_inundaciones = '../Metadata/Archivos_descargados/inundaciones.geojson'
comunas_rm = obtener_comunas_desde_geojson(archivo_inundaciones)

# Función para obtener coordenadas desde Nominatim
def obtener_coordenadas(comuna):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': f"{comuna}, Región Metropolitana, Chile",
        'format': 'json',
        'limit': 1,
    }
    headers = {
        'User-Agent': 'MiAplicacion/1.0 (tuemail@dominio.com)'  # Reemplazar con un email válido
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    if data:
        lat = data[0]['lat']
        lon = data[0]['lon']
        return lat, lon
    else:
        return None, None

# Función para obtener la precipitación desde la API de WeatherAPI
def obtener_precipitacion(lat, lon, api_key):
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        'key': api_key,
        'q': f"{lat},{lon}",
        'lang': 'es'
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'current' in data:
        precip_mm = data['current']['precip_mm']
        return precip_mm
    else:
        return None

# Lista para almacenar los resultados
resultados = []

# Limitar a 1 comuna para pruebas
for comuna in comunas_rm[:1]:  
    print(f"Procesando comuna: {comuna}")
    lat, lon = obtener_coordenadas(comuna)
    if lat and lon:
        precip_mm = obtener_precipitacion(lat, lon, api_key)
        if precip_mm is not None:
            resultados.append({
                'comuna': comuna,
                'latitud': lat,
                'longitud': lon,
                'precip_mm': precip_mm
            })
            print(f"Precipitación en {comuna}: {precip_mm} mm")
        else:
            print(f"No se pudo obtener la precipitación para {comuna}")
    else:
        print(f"No se pudieron obtener las coordenadas para {comuna}")
    time.sleep(1)  # Espera 1 segundo entre solicitudes a Nominatim

# Guardar los resultados en un archivo JSON
with open('./Archivos_descargados/precipitacion_comunas_rm.json', 'w', encoding='utf-8') as jsonfile:
    json.dump(resultados, jsonfile, ensure_ascii=False, indent=4)

print("Datos de precipitación guardados en 'precipitacion_comunas_rm.json'")
