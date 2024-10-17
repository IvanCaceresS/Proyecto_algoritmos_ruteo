import json
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
from shapely.geometry import shape, Point, LineString
from shapely import wkt

load_dotenv('../.env')

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

cur.execute("""
    ALTER TABLE proyectoalgoritmos.infraestructura 
    ADD COLUMN IF NOT EXISTS is_ciclovia BOOLEAN DEFAULT FALSE;
""")
cur.execute("""
    ALTER TABLE proyectoalgoritmos.infraestructura 
    ADD COLUMN IF NOT EXISTS oneway VARCHAR(3) DEFAULT 'no';
""")
conn.commit()

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
all_nodes = []
line_properties = []

def insert_node_if_not_exists(point_geom):
    cur.execute("SELECT id FROM proyectoalgoritmos.infraestructura_nodos WHERE ST_Equals(geometry, ST_GeomFromText(%s, 4326))", (point_geom.wkt,))
    result = cur.fetchone()
    
    if result:
        return result[0]
    else:
        cur.execute(insert_node_query, (point_geom.wkt,))
        node_id = cur.fetchone()[0]
        all_nodes.append(point_geom)
        return node_id

for feature in geojson_data['features']:
    geom = shape(feature['geometry'])
    if isinstance(geom, LineString):
        line_geometries.append(geom)

        properties = feature['properties']
        line_id = properties.get('id')
        name = properties.get('name', 'Sin nombre')
        highway_type = properties.get('highway', 'unknown')
        lanes = int(properties.get('lanes', 1))
        oneway = properties.get('oneway', 'no')
        
        line_properties.append((line_id, name, highway_type, lanes, oneway))

        start_point = Point(geom.coords[0])
        end_point = Point(geom.coords[-1])

        source_node_id = insert_node_if_not_exists(start_point)
        target_node_id = insert_node_if_not_exists(end_point)

        cost = geom.length
        if(len(oneway) > 3):
            oneway = 'no'
        cur.execute(insert_line_query, (
            line_id, name, highway_type, lanes, source_node_id, target_node_id, geom.wkt, cost, False, oneway
        ))

conn.commit()

def get_intersecting_nodes(line):
    intersecting_nodes = []
    cur.execute("SELECT id, ST_AsText(geometry) FROM proyectoalgoritmos.infraestructura_nodos")
    all_nodes_in_db = cur.fetchall()

    for node_id, node_geom_wkt in all_nodes_in_db:
        point = wkt.loads(node_geom_wkt)
        if line.distance(point) < 1e-8:
            intersecting_nodes.append((node_id, point))
    
    return intersecting_nodes

new_line_id = 1
for idx, line in enumerate(line_geometries):
    original_line_id, name, highway_type, lanes, oneway = line_properties[idx]

    intersecting_nodes = get_intersecting_nodes(line)

    intersecting_nodes = sorted(intersecting_nodes, key=lambda p: line.project(p[1]))

    if len(intersecting_nodes) > 1:
        for i in range(len(intersecting_nodes) - 1):
            segment = LineString([intersecting_nodes[i][1], intersecting_nodes[i + 1][1]])

            source_node_id = intersecting_nodes[i][0]
            target_node_id = intersecting_nodes[i + 1][0]

            cost = segment.length
            if(len(oneway) > 3):
                oneway = 'no'
            cur.execute(insert_line_query, (
                new_line_id, name, highway_type, lanes, source_node_id, target_node_id, segment.wkt, cost, False, oneway 
            ))

            new_line_id += 1 

conn.commit()

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
