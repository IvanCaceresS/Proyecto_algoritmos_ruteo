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

# Función para exportar una tabla a GeoJSON
def export_to_geojson(table_name, geometry_column, output_file):
    # Ejecutar una consulta para obtener las geometrías en formato GeoJSON
    cur.execute(f"""
        SELECT id, name, {geometry_column}, ST_AsGeoJSON({geometry_column}) AS geom_json
        FROM proyectoalgoritmos.{table_name};
    """)

    rows = cur.fetchall()

    features = []
    for row in rows:
        feature_id = row[0]
        name = row[1]
        geometry_json = row[3]

        # Crear la estructura GeoJSON
        geojson_feature = {
            "type": "Feature",
            "properties": {
                "id": feature_id,
                "name": name
            },
            "geometry": json.loads(geometry_json)
        }
        features.append(geojson_feature)

    # Crear el FeatureCollection
    geojson_result = {
        "type": "FeatureCollection",
        "features": features
    }

    # Guardar el resultado en un archivo GeoJSON
    with open(output_file, "w", encoding="utf-8") as geojson_file:
        json.dump(geojson_result, geojson_file, ensure_ascii=False, indent=4)

    print(f"Exportación completada: {output_file}")

# Exportar la tabla 'infraestructura' a un archivo GeoJSON
export_to_geojson('infraestructura', 'geometry', 'infraestructura.geojson')

# Exportar la tabla 'infraestructura_nodos' a un archivo GeoJSON
export_to_geojson('infraestructura_nodos', 'geometry', 'infraestructura_nodos.geojson')

# Cerrar la conexión
cur.close()
conn.close()
