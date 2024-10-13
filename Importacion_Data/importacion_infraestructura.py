import json
import psycopg2
from osgeo import ogr  # Librería para leer KML

# Conectar a la base de datos
conn = psycopg2.connect(
    host="localhost",
    database="mi_base_datos",
    user="mi_usuario",
    password="mi_contraseña"
)
cur = conn.cursor()

# Insertar datos del GeoJSON
with open('../Infraestructura/calles_primarias_secundarias_santiago.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

    for feature in geojson_data['features']:
        name = feature['properties'].get('name', None)
        lanes = feature['properties'].get('lanes', None)
        highway_type = feature['properties'].get('highway', None)
        coordinates = feature['geometry']['coordinates']

        # Formatear las coordenadas para que PostGIS las interprete correctamente
        line_string = "LINESTRING(" + ", ".join([f"{coord[0]} {coord[1]}" for coord in coordinates]) + ")"

        # Insertar los datos en la tabla
        cur.execute("""
            INSERT INTO infraestructura (name, type, lanes, geometry)
            VALUES (%s, %s, %s, ST_GeomFromText(%s, 4326))
        """, (name, highway_type, lanes, line_string))

# Insertar datos del KML (ciclovías)
kml_path = '../Infraestructura/ciclovias_santiago.kml'
driver = ogr.GetDriverByName('KML')
data_source = driver.Open(kml_path, 0)  # 0 significa que es de solo lectura

layer = data_source.GetLayer()

for feature in layer:
    name = feature.GetField('name')
    geometry = feature.GetGeometryRef()
    line_string = geometry.ExportToWkt()

    # Insertar los datos de ciclovías
    cur.execute("""
        INSERT INTO infraestructura (name, type, geometry)
        VALUES (%s, %s, ST_GeomFromText(%s, 4326))
    """, (name, 'ciclovía', line_string))

# Confirmar las transacciones y cerrar la conexión
conn.commit()
cur.close()
conn.close()
