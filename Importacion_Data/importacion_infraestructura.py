import json
import psycopg2
import xml.etree.ElementTree as ET
from shapely.geometry import LineString
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
print("Cargando variables de entorno...")
load_dotenv(dotenv_path='../.env')

host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

# Conectar a la base de datos
print(f"Conectando a la base de datos {database}...")
conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password
)
cur = conn.cursor()

# Parsear el archivo KML de ciclovías
kml_path = '../Infraestructura/Archivos_descargados/ciclovias_santiago.kml'
print(f"Procesando el archivo KML: {kml_path}...")
tree = ET.parse(kml_path)
root = tree.getroot()

namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
ciclovias = []

# Procesar ciclovías del archivo KML
print("Extrayendo coordenadas de ciclovías...")
for placemark in root.findall(".//kml:Placemark", namespace):
    coordinates_element = placemark.find(".//kml:coordinates", namespace)
    if coordinates_element is not None:
        coordinates_text = coordinates_element.text.strip()
        coord_pairs = coordinates_text.split()
        ciclovia_coords = [(float(coord.split(',')[0]), float(coord.split(',')[1])) for coord in coord_pairs]
        ciclovias.append(LineString(ciclovia_coords))
print(f"{len(ciclovias)} ciclovías procesadas.")

# Procesar el archivo GeoJSON de calles
geojson_path = '../Infraestructura/Archivos_descargados/calles_primarias_secundarias_santiago.geojson'
print(f"Procesando el archivo GeoJSON: {geojson_path}...")
with open(geojson_path, 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

    print("Insertando datos de infraestructura en la base de datos...")
    for feature in geojson_data['features']:
        feature_id = feature['properties'].get('id', None)
        
        if feature_id is None:
            print(f"Advertencia: El feature {feature['properties'].get('name', 'sin nombre')} no tiene 'id'.")
            continue

        name = feature['properties'].get('name', None)
        lanes = feature['properties'].get('lanes', None)
        highway_type = feature['properties'].get('highway', None)
        coordinates = feature['geometry']['coordinates']

        line_string_geom = LineString([(coord[0], coord[1]) for coord in coordinates])

        # Determinar si la línea intersecta alguna ciclovía
        is_ciclovia = any(line_string_geom.intersects(ciclovia) for ciclovia in ciclovias)

        line_string_wkt = line_string_geom.wkt

        # Insertar la línea de infraestructura en la tabla
        cur.execute("""
            INSERT INTO proyectoalgoritmos.infraestructura (id, name, type, lanes, is_ciclovia, geometry)
            VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))
        """, (feature_id, name, highway_type, lanes, is_ciclovia, line_string_wkt))

print("Datos de infraestructura insertados correctamente.")

# Detección de intersecciones (nodos) con tolerancia
print("Detectando intersecciones entre segmentos de infraestructura...")
cur.execute("""
    INSERT INTO proyectoalgoritmos.infraestructura_nodos (geometry)
    SELECT ST_Intersection(a.geometry, b.geometry) AS geometry
    FROM proyectoalgoritmos.infraestructura a, proyectoalgoritmos.infraestructura b
    WHERE a.id < b.id
    AND ST_Intersects(ST_Buffer(a.geometry, 0.00001), ST_Buffer(b.geometry, 0.00001))
    AND ST_GeometryType(ST_Intersection(a.geometry, b.geometry)) = 'ST_Point';
""")
conn.commit()
print("Intersecciones detectadas e insertadas correctamente.")

# Asignar los valores de 'source' y 'target' en base a los nodos más cercanos
print("Asignando nodos 'source' y 'target' a los segmentos de infraestructura...")
cur.execute("SELECT id, ST_AsText(geometry) FROM proyectoalgoritmos.infraestructura")
infraestructuras = cur.fetchall()

for infraestructura in infraestructuras:
    infraestructura_id = infraestructura[0]
    geometry = infraestructura[1]

    # Encontrar el nodo más cercano al punto inicial (source)
    cur.execute("""
        SELECT id 
        FROM proyectoalgoritmos.infraestructura_nodos 
        ORDER BY ST_Distance(geometry, ST_StartPoint(ST_GeomFromText(%s, 4326))) 
        LIMIT 1;
    """, (geometry,))
    source_result = cur.fetchone()

    # Encontrar el nodo más cercano al punto final (target)
    cur.execute("""
        SELECT id 
        FROM proyectoalgoritmos.infraestructura_nodos 
        ORDER BY ST_Distance(geometry, ST_EndPoint(ST_GeomFromText(%s, 4326))) 
        LIMIT 1;
    """, (geometry,))
    target_result = cur.fetchone()

    # Si ambos nodos existen, actualiza los valores de 'source' y 'target'
    if source_result and target_result:
        source_node = source_result[0]
        target_node = target_result[0]
        cur.execute("""
            UPDATE proyectoalgoritmos.infraestructura 
            SET source = %s, target = %s 
            WHERE id = %s;
        """, (source_node, target_node, infraestructura_id))

conn.commit()
print("Nodos 'source' y 'target' asignados correctamente.")

# Cerrar la conexión
cur.close()
conn.close()
print("Conexión cerrada y proceso finalizado.")
