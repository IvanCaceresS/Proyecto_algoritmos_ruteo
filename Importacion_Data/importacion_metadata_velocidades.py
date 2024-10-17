import psycopg2
import json
from dotenv import load_dotenv
import os
from shapely.geometry import shape

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

with open('../Metadata/Archivos_descargados/velocidades_maximas.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

insert_query = """
    INSERT INTO proyectoalgoritmos.velocidades_maximas (geojson_id, maxspeed, geometry)
    VALUES (%s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326))
"""

for feature in geojson_data['features']:
    geojson_id = feature.get('properties', {}).get('id')
    maxspeed = feature.get('properties', {}).get('maxspeed', None)

    geom = shape(feature['geometry'])

    if geom.geom_type == "LineString":
        wkt_geom = geom.wkt

        cur.execute(insert_query, (geojson_id, maxspeed, wkt_geom))

conn.commit()

cur.close()
conn.close()

print("Datos de velocidades máximas insertados correctamente en la tabla 'velocidades_maximas'.")
