import json
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv(dotenv_path=r'../.env')
CACHE_FILE = './Archivos_descargados/api_responses.json'

def cargar_datos_de_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print("No se encontraron datos en caché. Ejecuta cierre-calles.py para obtenerlos.")
        return []

def procesar_trafico(geojson_path):
    datos = cargar_datos_de_cache()
    if datos:
        df = pd.DataFrame(datos)
        df[['id', 'name', 'coordenada', 'current_speed', 'free_flow_speed']].to_json(
            './Archivos_descargados/trafico_actual.json', orient='records', force_ascii=False, indent=4
        )
    else:
        print("Sin datos para procesar el tráfico actual.")

geojson_path = r'../Infraestructura/Archivos_descargados/calles_primarias_secundarias_santiago.geojson'
procesar_trafico(geojson_path)
