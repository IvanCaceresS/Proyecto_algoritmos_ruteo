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
with open('../Amenazas/Archivos_descargados/seguridad.json', 'r', encoding='utf-8') as f:
    seguridad_data = json.load(f)

# Preparar la consulta de inserción
insert_query = """
    INSERT INTO proyectoalgoritmos.seguridad_comunas_rm (comuna, indice_delitos)
    VALUES (%s, %s)
"""

# Procesar los datos del archivo JSON
for comuna, indice_delitos in seguridad_data.items():
    # Convertir el valor del índice de delitos a float, reemplazando el punto por nada (miles) y la coma por un punto (decimales)
    indice_delitos_float = float(indice_delitos.replace('.', '').replace(',', '.').strip())

    # Insertar los datos en la tabla
    cur.execute(insert_query, (comuna, indice_delitos_float))

# Confirmar la inserción de los datos
conn.commit()

# Cerrar la conexión
cur.close()
conn.close()

print("Datos de seguridad de comunas insertados correctamente en la tabla 'seguridad_comunas_rm'.")
