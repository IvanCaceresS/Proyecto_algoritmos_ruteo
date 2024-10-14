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

# Preparar la consulta de selección
select_query = """
    SELECT comuna, latitud, longitud, precip_mm
    FROM proyectoalgoritmos.precipitacion_comunas_rm
"""

cur.execute(select_query)
rows = cur.fetchall()

# Lista para almacenar los resultados
resultados = []

# Procesar cada fila de la tabla y crear el formato adecuado
for row in rows:
    comuna_name = row[0]
    latitud = row[1]
    longitud = row[2]
    precip_mm = row[3]

    resultados.append({
        'comuna': comuna_name,
        'latitud': str(latitud),
        'longitud': str(longitud),
        'precip_mm': precip_mm
    })

# Crear el directorio si no existe
output_dir = './Archivos_exportados'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Guardar los resultados en un archivo JSON
output_file = os.path.join(output_dir, 'precipitacion_comunas_rm.json')
with open(output_file, 'w', encoding='utf-8') as jsonfile:
    json.dump(resultados, jsonfile, ensure_ascii=False, indent=4)

print(f"Datos de precipitación de comunas exportados a '{output_file}'.")
