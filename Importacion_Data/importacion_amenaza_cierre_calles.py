import psycopg2
import json
from dotenv import load_dotenv
import os
from shapely.geometry import Point

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

# Leer el archivo JSON
with open('../Amenazas/Archivos_descargados/cierres_calles.json', 'r', encoding='utf-8') as f:
    calles_data = json.load(f)

# Preparar la consulta de inserción
insert_query = """
    INSERT INTO proyectoalgoritmos.cierres_calles (id, name, coordenada, road_closure)
    VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
"""

# Procesar los datos del archivo JSON
for calle in calles_data:
    calle_id = calle.get('id')
    name = calle.get('name')
    coordenada = calle.get('coordenada').split(',')
    lat = float(coordenada[0])
    lon = float(coordenada[1])
    road_closure = calle.get('road_closure', 'No')

    # Insertar los datos en la tabla
    cur.execute(insert_query, (calle_id, name, lon, lat, road_closure))

# Confirmar la inserción de los datos
conn.commit()

# Cerrar la conexión
cur.close()
conn.close()

print("Datos de cierres de calles insertados correctamente en la tabla 'cierres_calles'.")
