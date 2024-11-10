import json
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
from shapely.geometry import shape, Point, LineString
from shapely import wkt

# Cargar variables de entorno
load_dotenv('../.env')

# Conexión a la base de datos
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

# Asegurar que las columnas adicionales existen
cur.execute("""
    ALTER TABLE proyectoalgoritmos.infraestructura 
    ADD COLUMN IF NOT EXISTS is_ciclovia BOOLEAN DEFAULT FALSE;
""")
cur.execute("""
    ALTER TABLE proyectoalgoritmos.infraestructura 
    ADD COLUMN IF NOT EXISTS oneway VARCHAR(3) DEFAULT 'no';
""")
conn.commit()

# Cargar datos GeoJSON
with open('../Infraestructura/Archivos_descargados/calles_primarias_secundarias_santiago.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

insert_node_query = sql.SQL("""
    INSERT INTO proyectoalgoritmos.infraestructura_nodos (geometry)
    VALUES (ST_GeomFromText(%s, 4326))
    RETURNING id
""")

insert_line_query = sql.SQL("""
    INSERT INTO proyectoalgoritmos.infraestructura (id, name, type, lanes, source, target, geometry, cost, is_ciclovia, oneway)
    VALUES (%s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326), %s, %s, %s)
""")

line_geometries = []
line_properties = []

# Función para ajustar el valor de oneway
def ajustar_oneway(valor):
    return valor if valor in ("yes", "no") else "no"  # Valor predeterminado para casos no válidos

# Obtener todos los nodos de infraestructura y almacenar sus geometrías
cur.execute("SELECT id, ST_AsText(geometry) FROM proyectoalgoritmos.infraestructura_nodos")
all_nodes_in_db = {wkt.loads(geom_wkt): node_id for node_id, geom_wkt in cur.fetchall()}

# Función para insertar o recuperar un nodo
def insert_node_if_not_exists(point_geom):
    if point_geom in all_nodes_in_db:
        return all_nodes_in_db[point_geom]
    else:
        cur.execute(insert_node_query, (point_geom.wkt,))
        node_id = cur.fetchone()[0]
        all_nodes_in_db[point_geom] = node_id
        return node_id

# Procesar las líneas del archivo GeoJSON
for feature in geojson_data['features']:
    geom = shape(feature['geometry'])
    if isinstance(geom, LineString):
        line_geometries.append(geom)

        properties = feature['properties']
        line_id = properties.get('id')
        name = properties.get('name', 'Sin nombre')
        highway_type = properties.get('highway', 'unknown')
        lanes = int(properties.get('lanes', 1))
        oneway = ajustar_oneway(properties.get('oneway', 'no'))
        
        line_properties.append((line_id, name, highway_type, lanes, oneway))

        start_point = Point(geom.coords[0])
        end_point = Point(geom.coords[-1])

        source_node_id = insert_node_if_not_exists(start_point)
        target_node_id = insert_node_if_not_exists(end_point)

        cost = geom.length
        cur.execute(insert_line_query, (
            line_id, name, highway_type, lanes, source_node_id, target_node_id, geom.wkt, cost, False, oneway
        ))

conn.commit()

# Dividir líneas en segmentos entre nodos de intersección
new_line_id = 1
for idx, line in enumerate(line_geometries):
    original_line_id, name, highway_type, lanes, oneway = line_properties[idx]

    # Filtrar nodos que estén lo suficientemente cerca y ordenar si line no está vacío
    intersecting_nodes = [
        (node_id, point) for point, node_id in all_nodes_in_db.items() if line.distance(point) < 1e-6
    ]
    if not line.is_empty:
        intersecting_nodes = sorted(intersecting_nodes, key=lambda p: line.project(p[1]))

    # Crear segmentos entre nodos de intersección
    if len(intersecting_nodes) > 1:
        for i in range(len(intersecting_nodes) - 1):
            segment = LineString([intersecting_nodes[i][1], intersecting_nodes[i + 1][1]])

            if segment.is_empty or not segment.is_valid:
                continue  # Omitir segmentos vacíos o no válidos

            source_node_id = intersecting_nodes[i][0]
            target_node_id = intersecting_nodes[i + 1][0]

            cost = segment.length
            cur.execute(insert_line_query, (
                new_line_id, name, highway_type, lanes, source_node_id, target_node_id, segment.wkt, cost, False, oneway 
            ))

            new_line_id += 1


conn.commit()

# Actualizar intersección con ciclovías en bloque
cur.execute("""
    UPDATE proyectoalgoritmos.infraestructura
    SET is_ciclovia = TRUE
    FROM proyectoalgoritmos.ciclovias
    WHERE ST_Intersects(proyectoalgoritmos.infraestructura.geometry, proyectoalgoritmos.ciclovias.geometry);
""")
conn.commit()

print("Las intersecciones con ciclovías han sido actualizadas.")

cur.close()
conn.close()
