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

def export_to_geojson(table_name, geometry_column, output_file, extra_columns=None):
    extra_columns_str = ', '.join(extra_columns) if extra_columns else ''
    columns = f"id, {extra_columns_str}, {geometry_column}, ST_AsGeoJSON({geometry_column}) AS geom_json" if extra_columns else f"id, {geometry_column}, ST_AsGeoJSON({geometry_column}) AS geom_json"

    cur.execute(f"""
        SELECT {columns}
        FROM proyectoalgoritmos.{table_name};
    """)

    rows = cur.fetchall()

    features = []
    for row in rows:
        feature_id = row[0]
        properties = {"id": feature_id}

        if extra_columns:
            for i, col in enumerate(extra_columns):
                properties[col] = row[i + 1]

        geometry_json = row[-1]

        geojson_feature = {
            "type": "Feature",
            "properties": properties,
            "geometry": json.loads(geometry_json)
        }
        features.append(geojson_feature)

    geojson_result = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(output_file, "w", encoding="utf-8") as geojson_file:
        json.dump(geojson_result, geojson_file, ensure_ascii=False, indent=4)

    print(f"Exportación completada: {output_file}")

export_to_geojson('estacionamientos', 'geometry', './Archivos_exportados/estacionamientos.geojson', extra_columns=['geojson_id', 'name', 'amenity', 'capacity', 'network'])

cur.close()
conn.close()
