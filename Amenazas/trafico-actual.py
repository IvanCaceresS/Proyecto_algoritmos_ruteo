import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=r'../.env')

API_KEY = os.getenv("TOMTOM_API_KEY")

def cargar_coordenadas(geojson_path):
    # Cargar el archivo GeoJSON usando json en lugar de geopandas
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    
    coordenadas = []
    for feature in geojson_data['features']:
        geometry = feature.get('geometry', {})
        properties = feature.get('properties', {})
        
        # Asegúrate de que la geometría es de tipo LineString
        if geometry.get('type') == 'LineString':
            primera_coordenada = geometry['coordinates'][0]
            coordenadas.append({
                'coordenada': f"{primera_coordenada[1]},{primera_coordenada[0]}",
                'id': properties.get('id', 'N/A'),
                'name': properties.get('name', 'N/A')
            })
    
    return coordenadas[:50]  # Limitar a 50 para no exceder el límite de llamadas a la API

def obtener_trafico_actual(point, api_key):
    url = 'https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/10/json'
    params = {
        'point': point['coordenada'],
        'unit': 'KMPH',
        'openLr': 'false',
        'key': api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        flow_data = data.get('flowSegmentData', {})
        current_speed = flow_data.get('currentSpeed', 'N/A')
        free_flow_speed = flow_data.get('freeFlowSpeed', 'N/A')
        return {
            'id': point['id'],
            'name': point['name'],
            'coordenada': point['coordenada'],
            'current_speed': current_speed,
            'free_flow_speed': free_flow_speed
        }
    else:
        print(f"Error al obtener el tráfico actual para la coordenada {point['coordenada']}: {response.status_code}")
        return None

def procesar_trafico(geojson_path, api_key):
    coordenadas = cargar_coordenadas(geojson_path)
    resultados = []
    for point in coordenadas:
        resultado = obtener_trafico_actual(point, api_key)
        if resultado:
            resultados.append(resultado)
    
    # Guardar los resultados en un archivo JSON
    with open(r'./Archivos_descargados/trafico_actual.json', 'w', encoding='utf-8') as jsonfile:
        json.dump(resultados, jsonfile, ensure_ascii=False, indent=4)

# Ruta al archivo GeoJSON
geojson_path = r'../Infraestructura/Archivos_descargados/calles_primarias_secundarias_santiago.geojson'

# Ejecutar el proceso
procesar_trafico(geojson_path, API_KEY)
