import json
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
from shapely.geometry import shape, Point, LineString
from shapely import wkt  # Importar para cargar geometría WKT

# Cargar credenciales desde archivo .env
load_dotenv('../.env')

# Conexión a la base de datos
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

# Agregar la columna 'is_ciclovia' a la tabla infraestructura si no existe
cur.execute("""
    ALTER TABLE proyectoalgoritmos.infraestructura 
    ADD COLUMN IF NOT EXISTS is_ciclovia BOOLEAN DEFAULT FALSE;
""")
conn.commit()

# Leer archivo GeoJSON
with open('../Infraestructura/Archivos_descargados/calles_primarias_secundarias_santiago.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

# Preparar las consultas de inserción
insert_node_query = sql.SQL("""
    INSERT INTO proyectoalgoritmos.infraestructura_nodos (geometry)
    VALUES (ST_GeomFromText(%s, 4326))
    RETURNING id
""")

insert_line_query = sql.SQL("""
    INSERT INTO proyectoalgoritmos.infraestructura (id, name, type, lanes, source, target, geometry, cost, is_ciclovia)
    VALUES (%s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326), %s, %s)
""")

# Crear una lista para todas las geometrías (líneas) del GeoJSON
line_geometries = []
all_nodes = []  # Lista para almacenar todos los nodos (Point geometries)
line_properties = []  # Lista para almacenar las propiedades de las líneas

# Función para insertar un nodo si no existe y retornar su id
def insert_node_if_not_exists(point_geom):
    cur.execute("SELECT id FROM proyectoalgoritmos.infraestructura_nodos WHERE ST_Equals(geometry, ST_GeomFromText(%s, 4326))", (point_geom.wkt,))
    result = cur.fetchone()
    
    if result:
        return result[0]  # Nodo ya existe, retornar su id
    else:
        # Insertar nodo si no existe
        cur.execute(insert_node_query, (point_geom.wkt,))
        node_id = cur.fetchone()[0]
        all_nodes.append(point_geom)  # Añadir el nodo a la lista global
        return node_id

# Procesar los features del GeoJSON y extraer las geometrías
for feature in geojson_data['features']:
    geom = shape(feature['geometry'])  # Convertir a objeto Shapely
    if isinstance(geom, LineString):  # Solo procesar LineStrings
        line_geometries.append(geom)

        # Extraer propiedades y almacenarlas junto con la línea
        properties = feature['properties']
        line_id = properties.get('id')
        name = properties.get('name', 'Sin nombre')
        highway_type = properties.get('highway', 'unknown')
        lanes = int(properties.get('lanes', 1))
        
        # Guardar las propiedades de la línea para luego usarlas en cada segmento
        line_properties.append((line_id, name, highway_type, lanes))

        # Insertar puntos de inicio y fin como nodos
        start_point = Point(geom.coords[0])
        end_point = Point(geom.coords[-1])

        # Insertar o encontrar los nodos existentes
        source_node_id = insert_node_if_not_exists(start_point)
        target_node_id = insert_node_if_not_exists(end_point)

        # Calcular la longitud de la línea (distancia)
        cost = geom.length

        # Insertar la línea original en la tabla (esto será eliminado después)
        cur.execute(insert_line_query, (
            line_id, name, highway_type, lanes, source_node_id, target_node_id, geom.wkt, cost, False  # Ciclovía inicialmente como False
        ))

# Confirmar la inserción de las líneas
conn.commit()

# Función para encontrar los nodos que intersectan una línea
def get_intersecting_nodes(line):
    intersecting_nodes = []
    cur.execute("SELECT id, ST_AsText(geometry) FROM proyectoalgoritmos.infraestructura_nodos")
    all_nodes_in_db = cur.fetchall()

    for node_id, node_geom_wkt in all_nodes_in_db:
        point = wkt.loads(node_geom_wkt)  # Convertir de WKT a un objeto Point de Shapely
        if line.distance(point) < 1e-8:  # Si el nodo toca la línea
            intersecting_nodes.append((node_id, point))
    
    return intersecting_nodes

# Ahora procesamos la atomización de las líneas
new_line_id = 1
for idx, line in enumerate(line_geometries):
    # Obtener las propiedades de la línea original
    original_line_id, name, highway_type, lanes = line_properties[idx]

    # Obtener los nodos que tocan esta línea (consultamos en la tabla)
    intersecting_nodes = get_intersecting_nodes(line)

    # Ordenar los nodos por su posición en la línea
    intersecting_nodes = sorted(intersecting_nodes, key=lambda p: line.project(p[1]))

    # Dividir la línea en segmentos entre cada par de nodos consecutivos
    if len(intersecting_nodes) > 1:
        for i in range(len(intersecting_nodes) - 1):
            segment = LineString([intersecting_nodes[i][1], intersecting_nodes[i + 1][1]])

            # Obtener los IDs de los nodos source y target para este segmento
            source_node_id = intersecting_nodes[i][0]
            target_node_id = intersecting_nodes[i + 1][0]

            # Calcular la longitud del segmento (distancia)
            cost = segment.length

            # Insertar el segmento como una nueva línea en la tabla infraestructura
            cur.execute(insert_line_query, (
                new_line_id, name, highway_type, lanes, source_node_id, target_node_id, segment.wkt, cost, False  # Ciclovía inicialmente como False
            ))

            new_line_id += 1  # Incrementar el ID de la nueva línea

# Confirmar la transacción
conn.commit()
print("Intersectando con ciclovías...")
# Intersección con ciclovías
cur.execute("""
    UPDATE proyectoalgoritmos.infraestructura
    SET is_ciclovia = TRUE
    FROM proyectoalgoritmos.ciclovias
    WHERE ST_Intersects(proyectoalgoritmos.infraestructura.geometry, proyectoalgoritmos.ciclovias.geometry);
""")
conn.commit()

print("Las intersecciones con ciclovías han sido actualizadas.")

# Cerrar la conexión
cur.close()
conn.close()
