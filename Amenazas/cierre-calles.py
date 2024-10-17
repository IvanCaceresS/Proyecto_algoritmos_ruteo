import requests
import geopandas as gpd
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=r'../.env')

API_KEY = os.getenv("TOMTOM_API_KEY")

def cargar_coordenadas(geojson_path):
    gdf = gpd.read_file(geojson_path)
    coordenadas = []
    for _, feature in gdf.iterrows():
        if feature.geometry.geom_type == 'LineString':
            primera_coordenada = feature.geometry.coords[0]
            coordenadas.append({
                'coordenada': f"{primera_coordenada[1]},{primera_coordenada[0]}",
                'id': feature['id'],
                'name': feature.get('name', 'N/A')
            })
    return coordenadas[:50] # Limitar a 10 para no exceder el límite de llamadas a la API

def obtener_cierres_calles(point, api_key):
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
        road_closure = flow_data.get('roadClosure', False)
        return {
            'id': point['id'],
            'name': point['name'],
            'coordenada': point['coordenada'],
            'road_closure': 'Sí' if road_closure else 'No'
        }
    else:
        print(f"Error al obtener el estado de cierre de calles para la coordenada {point['coordenada']}: {response.status_code}")
        return None

def procesar_cierres_calles(geojson_path, api_key):
    coordenadas = cargar_coordenadas(geojson_path)
    resultados = []
    for point in coordenadas:
        resultado = obtener_cierres_calles(point, api_key)
        if resultado:
            resultados.append(resultado)
    df = pd.DataFrame(resultados)
    
    df.to_json(r'./Archivos_descargados/cierres_calles.json', orient='records', force_ascii=False, indent=4)

geojson_path = r'../Infraestructura/Archivos_descargados/calles_primarias_secundarias_santiago.geojson'

procesar_cierres_calles(geojson_path, API_KEY)