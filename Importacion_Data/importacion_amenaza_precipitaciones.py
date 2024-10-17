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

with open('../Amenazas/Archivos_descargados/precipitacion_comunas_rm.json', 'r', encoding='utf-8') as f:
    precipitacion_data = json.load(f)

insert_query = """
    INSERT INTO proyectoalgoritmos.precipitacion_comunas_rm (comuna, latitud, longitud, precip_mm)
    VALUES (%s, %s, %s, %s)
"""

for comuna in precipitacion_data:
    comuna_name = comuna.get('comuna')
    latitud = float(comuna.get('latitud'))
    longitud = float(comuna.get('longitud'))
    precip_mm = float(comuna.get('precip_mm'))

    cur.execute(insert_query, (comuna_name, latitud, longitud, precip_mm))

conn.commit()

cur.close()
conn.close()

print("Datos de precipitación de comunas insertados correctamente en la tabla 'precipitacion_comunas_rm'.")
