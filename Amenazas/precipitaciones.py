import requests
import time
import json
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv(dotenv_path='../.env')
api_key = os.getenv("WEATHER_API_KEY")

def obtener_comunas_desde_geojson(archivo_geojson):
    with open(archivo_geojson, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    comunas = set()
    for feature in data['features']:
        properties = feature.get('properties', {})
        comuna = properties.get('Comuna', None)  # Ajuste aquí según el nombre de la clave en 13.geojson
        if comuna:
            comunas.add(comuna)
    
    return list(comunas)

# Cambiar el archivo a 13.geojson para obtener las comunas específicas
archivo_geojson = '../Infraestructura/Archivos_descargados/13.geojson'
comunas_rm = obtener_comunas_desde_geojson(archivo_geojson)

def obtener_coordenadas(comuna):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': f"{comuna}, Región Metropolitana, Chile",
        'format': 'json',
        'limit': 1,
    }
    headers = {
        'User-Agent': 'MiAplicacion/1.0 (tuemail@dominio.com)'
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    if data:
        lat = data[0]['lat']
        lon = data[0]['lon']
        return lat, lon
    else:
        return None, None

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

resultados = []

# Procesar cada comuna extraída de 13.geojson
for comuna in comunas_rm:
    comuna = comuna.upper()
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
    time.sleep(1)  # Retraso para evitar saturación de la API

# Guardar resultados en un archivo JSON
with open('./Archivos_descargados/precipitacion_comunas_rm.json', 'w', encoding='utf-8') as jsonfile:
    json.dump(resultados, jsonfile, ensure_ascii=False, indent=4)

print("Datos de precipitación guardados en 'precipitacion_comunas_rm.json'")
