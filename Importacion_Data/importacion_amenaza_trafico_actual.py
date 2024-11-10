import psycopg2
import json
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='../.env')

host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password
)
cur = conn.cursor()

#Verificicar si archivo existe
if not os.path.exists('../Amenazas/Archivos_descargados/trafico_actual.json'):
    print("No se encontró el archivo 'trafico_actual.json'.")
    exit()
with open('../Amenazas/Archivos_descargados/trafico_actual.json', 'r', encoding='utf-8') as f:
    trafico_data = json.load(f)

insert_query = """
    INSERT INTO proyectoalgoritmos.trafico_actual (id, name, coordenada, current_speed, free_flow_speed)
    VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s)
"""

for segmento in trafico_data:
    segmento_id = segmento.get('id')
    name = segmento.get('name')
    coordenada = segmento.get('coordenada').split(',')
    lat = float(coordenada[0])
    lon = float(coordenada[1])
    current_speed = segmento.get('current_speed')
    free_flow_speed = segmento.get('free_flow_speed')

    cur.execute(insert_query, (segmento_id, name, lon, lat, current_speed, free_flow_speed))

conn.commit()

cur.close()
conn.close()

print("Datos de tráfico actual insertados correctamente en la tabla 'trafico_actual'.")
