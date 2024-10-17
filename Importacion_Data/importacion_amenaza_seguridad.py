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

with open('../Amenazas/Archivos_descargados/seguridad.json', 'r', encoding='utf-8') as f:
    seguridad_data = json.load(f)

insert_query = """
    INSERT INTO proyectoalgoritmos.seguridad_comunas_rm (comuna, indice_delitos)
    VALUES (%s, %s)
"""

for comuna, indice_delitos in seguridad_data.items():
    indice_delitos_float = float(indice_delitos.replace('.', '').replace(',', '.').strip())

    cur.execute(insert_query, (comuna, indice_delitos_float))

conn.commit()

cur.close()
conn.close()

print("Datos de seguridad de comunas insertados correctamente en la tabla 'seguridad_comunas_rm'.")
