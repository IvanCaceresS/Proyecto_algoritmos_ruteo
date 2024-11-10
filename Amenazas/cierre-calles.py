import requests
import json
import pandas as pd
import time
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv(dotenv_path=r'../.env')
API_KEY = os.getenv("TOMTOM_API_KEY")
CACHE_FILE = './Archivos_descargados/api_responses_cache.json'
REQUEST_LIMIT = 100  # Limitar a 100 solicitudes

# Cargar la caché de respuestas previas
def cargar_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Guardar la caché actualizada
def guardar_cache(cache):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)

# Cargar coordenadas desde el archivo GeoJSON con un límite especificado
def cargar_coordenadas(geojson_path, limit=100):
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    
    coordenadas = []
    for feature in geojson_data['features']:
        geometry = feature.get('geometry', {})
        properties = feature.get('properties', {})
        if geometry.get('type') == 'LineString':
            primera_coordenada = geometry['coordinates'][0]
            coordenadas.append({
                'coordenada': f"{primera_coordenada[1]},{primera_coordenada[0]}",
                'id': properties.get('id', 'N/A'),
                'name': properties.get('name', 'N/A')
            })
    
    return coordenadas[:limit]  # Limitar el número de coordenadas

# Obtener el estado de cierre y tráfico para un punto específico, verificando la caché primero
def obtener_cierre_y_trafico(point, api_key, cache):
    if point['coordenada'] in cache:
        return cache[point['coordenada']]

    url = 'https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/10/json'
    params = {'point': point['coordenada'], 'unit': 'KMPH', 'openLr': 'false', 'key': api_key}
    response = requests.get(url, params=params)

    # Control de rate limit para evitar bloqueos de la API
    if response.status_code == 429:
        print("Límite de peticiones alcanzado. Esperando 60 segundos.")
        time.sleep(60)  # Pausa de 1 minuto
        response = requests.get(url, params=params)

    # Manejar error 403 indicando al usuario que verifique el acceso a la API
    if response.status_code == 403:
        print(f"Acceso denegado para la coordenada {point['coordenada']}. Verifica tu API_KEY y límite de peticiones.")
        return None

    if response.status_code == 200:
        data = response.json().get('flowSegmentData', {})
        result = {
            'id': point['id'],
            'name': point['name'],
            'coordenada': point['coordenada'],
            'road_closure': 'Sí' if data.get('roadClosure') else 'No',
            'current_speed': data.get('currentSpeed', 'N/A'),
            'free_flow_speed': data.get('freeFlowSpeed', 'N/A')
        }
        cache[point['coordenada']] = result
        return result
    else:
        print(f"Error al obtener datos para la coordenada {point['coordenada']}: {response.status_code}")
        return None

# Procesar los cierres de calles y tráfico, usando caché y control de límite de peticiones
def procesar_cierres_calles_y_trafico(geojson_path, api_key, limit=100):
    coordenadas = cargar_coordenadas(geojson_path, limit=limit)
    resultados = []
    cache = cargar_cache()

    # Realizar las solicitudes de manera secuencial con una pausa entre cada solicitud
    for i, point in enumerate(coordenadas):
        if i >= REQUEST_LIMIT:
            print("Se ha alcanzado el límite de peticiones configurado.")
            break

        resultado = obtener_cierre_y_trafico(point, api_key, cache)
        if resultado:
            resultados.append(resultado)
        
        # Pausa de 0.5 segundos entre cada solicitud
        #time.sleep(0.5)

    # Guardar en caché para futuras ejecuciones
    guardar_cache(cache)

    # Verificar si hay resultados antes de guardar
    if resultados:
        df = pd.DataFrame(resultados)
        df[['id', 'name', 'coordenada', 'road_closure']].to_json(
            './Archivos_descargados/cierres_calles.json', orient='records', force_ascii=False, indent=4
        )
        df[['id', 'name', 'coordenada', 'current_speed', 'free_flow_speed']].to_json(
            './Archivos_descargados/trafico_actual.json', orient='records', force_ascii=False, indent=4
        )
        print("Datos guardados en archivos JSON.")
    else:
        print("No se encontraron resultados. Verifica el acceso a la API y el límite de peticiones.")

# Ruta al archivo GeoJSON
geojson_path = r'../Infraestructura/Archivos_descargados/calles_primarias_secundarias_santiago.geojson'
procesar_cierres_calles_y_trafico(geojson_path, API_KEY, limit=100)
