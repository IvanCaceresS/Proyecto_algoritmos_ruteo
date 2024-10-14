import psycopg2
import json
import re  # Librería para manejar expresiones regulares
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
with open('../Metadata/Archivos_descargados/estacionamientos.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

# Preparar la consulta de inserción
insert_query = """
    INSERT INTO proyectoalgoritmos.estacionamientos (geojson_id, name, amenity, capacity, network, geometry)
    VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326))
"""

# Función para extraer solo los números del campo 'capacity'
def extract_capacity(value):
    if value:
        match = re.search(r'\d+', value)  # Buscar los dígitos en la cadena
        if match:
            return int(match.group(0))  # Convertir el primer grupo encontrado a entero
    return None  # Si no se encuentra ningún número, devolver None

# Procesar las características (features) del archivo GeoJSON
for feature in geojson_data['features']:
    geojson_id = feature.get('id')
    properties = feature.get('properties', {})
    name = properties.get('name', 'Sin nombre')
    amenity = properties.get('amenity')
    capacity = extract_capacity(properties.get('capacity'))  # Usar la función para extraer números
    network = properties.get('network', None)
    
    # Obtener la geometría en formato WKT (Well-Known Text)
    geom = shape(feature['geometry'])

    # Filtrar solo las geometrías de tipo Point
    if geom.geom_type == "Point":
        wkt_geom = geom.wkt  # Convertir la geometría a WKT

        # Insertar los datos en la tabla
        cur.execute(insert_query, (geojson_id, name, amenity, capacity, network, wkt_geom))

# Confirmar la inserción de los datos
conn.commit()

# Cerrar la conexión
cur.close()
conn.close()

print("Datos insertados correctamente en la tabla 'estacionamientos'.")
