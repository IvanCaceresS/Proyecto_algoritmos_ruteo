import psycopg2
import json
from decimal import Decimal
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

# Función para convertir Decimals a float y manejar valores None
def convert_decimal(value):
    if value is None:  # Si el valor es None, lo devuelve tal cual
        return None
    if isinstance(value, Decimal):  # Si es Decimal, convertir a float
        return float(value)
    return value  # De lo contrario, devolver el valor original

# Función para exportar la tabla 'inundaciones' a GeoJSON
def export_to_geojson(table_name, geometry_column, output_file, extra_columns=None):
    # Extraer columnas adicionales, si se proporcionan
    extra_columns_str = ', '.join(extra_columns) if extra_columns else ''
    columns = f"id, {extra_columns_str}, {geometry_column}, ST_AsGeoJSON({geometry_column}) AS geom_json" if extra_columns else f"id, {geometry_column}, ST_AsGeoJSON({geometry_column}) AS geom_json"

    # Ejecutar una consulta para obtener las geometrías en formato GeoJSON
    cur.execute(f"""
        SELECT {columns}
        FROM proyectoalgoritmos.{table_name};
    """)

    rows = cur.fetchall()

    features = []
    for row in rows:
        feature_id = row[0]
        properties = {"id": feature_id}

        # Agregar las propiedades adicionales si las hay
        if extra_columns:
            for i, col in enumerate(extra_columns):
                properties[col] = convert_decimal(row[i + 1])  # Convertir Decimal o manejar None

        geometry_json = row[-1]  # La geometría GeoJSON está al final de cada fila

        # Crear la estructura GeoJSON
        geojson_feature = {
            "type": "Feature",
            "properties": properties,
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

# Exportar la tabla 'inundaciones' a un archivo GeoJSON
export_to_geojson('inundaciones', 'geometry', './Archivos_exportados/inundaciones.geojson', extra_columns=['nom_region', 'nom_comuna', 'nom_provin', 'ind_riesgo_inundaciones_t10_delta'])

# Cerrar la conexión
cur.close()
conn.close()
