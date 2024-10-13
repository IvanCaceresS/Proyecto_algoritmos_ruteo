# Requiere instalar requests, geopandas y pandas: pip install requests geopandas pandas
import requests
import geopandas as gpd
import pandas as pd

# Reemplaza con tu clave de API de TomTom
API_KEY = 'HjAS73C3c2bZnrPs7xrFbibOCiiRjKAz'

# Cargar archivo GeoJSON con coordenadas de calles
def cargar_coordenadas(geojson_path):
    gdf = gpd.read_file(geojson_path)
    coordenadas = []
    for _, feature in gdf.iterrows():
        if feature.geometry.type == 'LineString':
            # Obtener la primera coordenada de cada Feature de tipo LineString
            primera_coordenada = feature.geometry.coords[0]
            coordenadas.append({
                'coordenada': f"{primera_coordenada[1]},{primera_coordenada[0]}",
                'id': feature['id'],
                'name': feature.get('name', 'N/A')
            })
    return coordenadas[:10]  # Solo retornar las primeras 10 coordenadas

# 1. Obtener el tráfico actual y crear CSV
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

# Ejecutar la función para obtener el tráfico actual para todas las coordenadas del archivo GeoJSON y guardar en CSV
def procesar_trafico(geojson_path, api_key):
    coordenadas = cargar_coordenadas(geojson_path)
    resultados = []
    for point in coordenadas:
        resultado = obtener_trafico_actual(point, api_key)
        if resultado:
            resultados.append(resultado)
    df = pd.DataFrame(resultados)
    df.to_csv('./Archivos_descargados/trafico_actual.csv', index=False)

# Ruta al archivo GeoJSON
geojson_path = '..\Infraestructura\Archivos_descargados\calles_primarias_secundarias_santiago.geojson'

# Ejecutar funciones
procesar_trafico(geojson_path, API_KEY)
