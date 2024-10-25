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

select_query = """
    SELECT id, name, ST_AsText(coordenada) AS coordenada, current_speed, free_flow_speed
    FROM proyectoalgoritmos.trafico_actual
"""

cur.execute(select_query)
rows = cur.fetchall()

resultados = []

for row in rows:
    segmento_id = row[0]
    name = row[1]
    coordenada_wkt = row[2]
    current_speed = row[3]
    free_flow_speed = row[4]

    coordenada_wkt = coordenada_wkt.replace('POINT(', '').replace(')', '').split()
    lon = coordenada_wkt[0]
    lat = coordenada_wkt[1]

    resultados.append({
        'id': segmento_id,
        'name': name,
        'coordenada': f"{lat},{lon}",
        'current_speed': current_speed,
        'free_flow_speed': free_flow_speed
    })

output_dir = './Archivos_exportados'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file = os.path.join(output_dir, 'trafico_actual.json')
with open(output_file, 'w', encoding='utf-8') as jsonfile:
    json.dump(resultados, jsonfile, ensure_ascii=False, indent=4)

print(f"Datos de tráfico actual exportados a '{output_file}'.")
