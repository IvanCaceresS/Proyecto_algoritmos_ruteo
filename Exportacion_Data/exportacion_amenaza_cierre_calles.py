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
    SELECT id, name, ST_AsText(coordenada) AS coordenada, road_closure
    FROM proyectoalgoritmos.cierres_calles
"""

cur.execute(select_query)
rows = cur.fetchall()

resultados = []

for row in rows:
    calle_id = row[0]
    name = row[1]
    coordenada_wkt = row[2]
    road_closure = row[3]

    coordenada_wkt = coordenada_wkt.replace('POINT(', '').replace(')', '').split()
    lon = coordenada_wkt[0]
    lat = coordenada_wkt[1]

    resultados.append({
        'id': calle_id,
        'name': name,
        'coordenada': f"{lat},{lon}",
        'road_closure': road_closure
    })

with open('./Archivos_exportados/cierres_calles.json', 'w', encoding='utf-8') as jsonfile:
    json.dump(resultados, jsonfile, ensure_ascii=False, indent=4)

print("Datos de cierres de calles exportados a 'cierres_calles_exportado.json'.")
