import psycopg2
import json
from dotenv import load_dotenv
import os

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
with open('../Amenazas/Archivos_descargados/trafico_actual.json', 'r', encoding='utf-8') as f:
    trafico_data = json.load(f)

# Preparar la consulta de inserción
insert_query = """
    INSERT INTO proyectoalgoritmos.trafico_actual (id, name, coordenada, current_speed, free_flow_speed)
    VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s)
"""

# Procesar los datos del archivo JSON
for segmento in trafico_data:
    segmento_id = segmento.get('id')
    name = segmento.get('name')
    coordenada = segmento.get('coordenada').split(',')
    lat = float(coordenada[0])
    lon = float(coordenada[1])
    current_speed = segmento.get('current_speed')
    free_flow_speed = segmento.get('free_flow_speed')

    # Insertar los datos en la tabla
    cur.execute(insert_query, (segmento_id, name, lon, lat, current_speed, free_flow_speed))

# Confirmar la inserción de los datos
conn.commit()

# Cerrar la conexión
cur.close()
conn.close()

print("Datos de tráfico actual insertados correctamente en la tabla 'trafico_actual'.")
