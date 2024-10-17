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

with open('../Metadata/Archivos_descargados/inundaciones.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

insert_query = """
    INSERT INTO proyectoalgoritmos.inundaciones (nom_region, nom_comuna, nom_provin, ind_riesgo_inundaciones_t10_delta, geometry)
    VALUES (%s, %s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326))
"""

for feature in geojson_data['features']:
    properties = feature.get('properties', {})
    nom_region = properties.get('NOM_REGION')
    nom_comuna = properties.get('NOM_COMUNA')
    nom_provin = properties.get('NOM_PROVIN')
    ind_riesgo = properties.get('ind_riesgo_inundaciones_t10_delta')

    geom = shape(feature['geometry'])

    if geom.geom_type == "Polygon":
        wkt_geom = geom.wkt 

        cur.execute(insert_query, (nom_region, nom_comuna, nom_provin, ind_riesgo, wkt_geom))

conn.commit()

cur.close()
conn.close()

print("Datos de inundaciones insertados correctamente en la tabla 'inundaciones'.")
