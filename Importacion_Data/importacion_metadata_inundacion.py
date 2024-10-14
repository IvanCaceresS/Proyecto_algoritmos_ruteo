import psycopg2
import json
from dotenv import load_dotenv
import os
from shapely.geometry import shape

# Cargar las variables de entorno desde el archivo .env
load_dotenv(dotenv_path='../.env')

host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

# Conectar a la base de datos
conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password
)
cur = conn.cursor()

# Leer el archivo GeoJSON
with open('../Metadata/Archivos_descargados/inundaciones.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

# Preparar la consulta de inserción
insert_query = """
    INSERT INTO proyectoalgoritmos.inundaciones (nom_region, nom_comuna, nom_provin, ind_riesgo_inundaciones_t10_delta, geometry)
    VALUES (%s, %s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326))
"""

# Procesar las características (features) del archivo GeoJSON
for feature in geojson_data['features']:
    properties = feature.get('properties', {})
    nom_region = properties.get('NOM_REGION')
    nom_comuna = properties.get('NOM_COMUNA')
    nom_provin = properties.get('NOM_PROVIN')
    ind_riesgo = properties.get('ind_riesgo_inundaciones_t10_delta')

    # Obtener la geometría en formato WKT (Well-Known Text)
    geom = shape(feature['geometry'])

    # Filtrar solo las geometrías de tipo Polygon
    if geom.geom_type == "Polygon":
        wkt_geom = geom.wkt  # Convertir la geometría a WKT

        # Insertar los datos en la tabla
        cur.execute(insert_query, (nom_region, nom_comuna, nom_provin, ind_riesgo, wkt_geom))

# Confirmar la inserción de los datos
conn.commit()

# Cerrar la conexión
cur.close()
conn.close()

print("Datos de inundaciones insertados correctamente en la tabla 'inundaciones'.")
