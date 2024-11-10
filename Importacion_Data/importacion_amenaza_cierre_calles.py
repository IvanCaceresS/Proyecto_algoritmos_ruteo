import psycopg2
import json
from dotenv import load_dotenv
import os
from shapely.geometry import Point

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
#vERIFICAR SI JSON EXISTE
if not os.path.exists('../Amenazas/Archivos_descargados/cierres_calles.json'):
    print("No se encontró el archivo 'cierres_calles.json'. Por favor, descargue el archivo y vuelva a ejecutar el script.")
    exit()
with open('../Amenazas/Archivos_descargados/cierres_calles.json', 'r', encoding='utf-8') as f:
    calles_data = json.load(f)

insert_query = """
    INSERT INTO proyectoalgoritmos.cierres_calles (id, name, coordenada, road_closure)
    VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
"""

for calle in calles_data:
    calle_id = calle.get('id')
    name = calle.get('name')
    coordenada = calle.get('coordenada').split(',')
    lat = float(coordenada[0])
    lon = float(coordenada[1])
    road_closure = calle.get('road_closure', 'No')

    cur.execute(insert_query, (calle_id, name, lon, lat, road_closure))

conn.commit()

cur.close()
conn.close()

print("Datos de cierres de calles insertados correctamente en la tabla 'cierres_calles'.")
