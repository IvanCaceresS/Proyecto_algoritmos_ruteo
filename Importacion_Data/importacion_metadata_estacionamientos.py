import psycopg2
import json
import re
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

with open('../Metadata/Archivos_descargados/estacionamientos.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

insert_query = """
    INSERT INTO proyectoalgoritmos.estacionamientos (geojson_id, name, amenity, capacity, network, geometry)
    VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326))
"""

def extract_capacity(value):
    if value:
        match = re.search(r'\d+', value)
        if match:
            return int(match.group(0))
    return None

for feature in geojson_data['features']:
    geojson_id = feature.get('id')
    properties = feature.get('properties', {})
    name = properties.get('name', 'Sin nombre')
    amenity = properties.get('amenity')
    capacity = extract_capacity(properties.get('capacity'))
    network = properties.get('network', None)
    
    geom = shape(feature['geometry'])

    if geom.geom_type == "Point":
        wkt_geom = geom.wkt

        cur.execute(insert_query, (geojson_id, name, amenity, capacity, network, wkt_geom))

conn.commit()

cur.close()
conn.close()

print("Datos insertados correctamente en la tabla 'estacionamientos'.")
