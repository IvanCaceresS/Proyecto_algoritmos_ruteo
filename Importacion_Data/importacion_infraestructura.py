import json
import psycopg2
import xml.etree.ElementTree as ET
from shapely.geometry import LineString
from dotenv import load_dotenv
import os

# Función para cargar las ciclovías desde un archivo KML
def cargar_ciclovias(kml_path):
    try:
        print(f"Procesando el archivo KML: {kml_path}...")
        tree = ET.parse(kml_path)
        root = tree.getroot()

        namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
        ciclovias = []

        print("Extrayendo coordenadas de ciclovías...")
        for placemark in root.findall(".//kml:Placemark", namespace):
            coordinates_element = placemark.find(".//kml:coordinates", namespace)
            if coordinates_element is not None:
                coordinates_text = coordinates_element.text.strip()
                coord_pairs = coordinates_text.split()
                ciclovia_coords = [(float(coord.split(',')[0]), float(coord.split(',')[1])) for coord in coord_pairs]
                ciclovias.append(LineString(ciclovia_coords))
        print(f"{len(ciclovias)} ciclovías procesadas.")
        return ciclovias
    except Exception as e:
        print(f"Error procesando el archivo KML: {e}")
        return []

# Función para cargar y procesar las calles desde un archivo GeoJSON
def procesar_calles(geojson_path, ciclovias, cursor):
    try:
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

            # Crear la geometría LineString con las coordenadas
            line_string_geom = LineString([(coord[0], coord[1]) for coord in coordinates])

            # Determinar si la línea intersecta alguna ciclovía
            is_ciclovia = any(line_string_geom.intersects(ciclovia) for ciclovia in ciclovias)

            # Calcular el costo como la longitud de la geometría
            cost = line_string_geom.length  # Esto calcula la longitud en unidades de coordenadas (grados)

            # Si estás usando un sistema de coordenadas geográficas como EPSG:4326, podrías convertirlo a distancia en metros:
            # Por ejemplo, si quieres calcular la longitud en metros, necesitarías transformar la geometría a un sistema métrico (EPSG:3857) antes de calcular la longitud.
            # from shapely.ops import transform
            # from functools import partial
            # import pyproj
            # project = partial(pyproj.transform, pyproj.Proj(init='epsg:4326'), pyproj.Proj(init='epsg:3857'))
            # line_string_geom_meters = transform(project, line_string_geom)
            # cost = line_string_geom_meters.length  # Longitud en metros

            line_string_wkt = line_string_geom.wkt

            # Insertar la línea de infraestructura en la tabla con el costo calculado
            cursor.execute("""
                INSERT INTO proyectoalgoritmos.infraestructura (id, name, type, lanes, is_ciclovia, cost, geometry)
                VALUES (%s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))
            """, (feature_id, name, highway_type, lanes, is_ciclovia, cost, line_string_wkt))

        print("Datos de infraestructura insertados correctamente.")
    except Exception as e:
        print(f"Error procesando el archivo GeoJSON: {e}")


# Función para detectar intersecciones entre las calles
def detectar_intersecciones(cursor):
    try:
        print("Detectando intersecciones entre segmentos de infraestructura...")
        cursor.execute("""
            INSERT INTO proyectoalgoritmos.infraestructura_nodos (geometry)
            SELECT ST_Intersection(a.geometry, b.geometry) AS geometry
            FROM proyectoalgoritmos.infraestructura a, proyectoalgoritmos.infraestructura b
            WHERE a.id < b.id
            AND ST_DWithin(a.geometry, b.geometry, 0.00001)
            AND ST_GeometryType(ST_Intersection(a.geometry, b.geometry)) = 'ST_Point';
        """)
        print("Intersecciones detectadas e insertadas correctamente.")
    except Exception as e:
        print(f"Error detectando intersecciones: {e}")

# Función para asignar los nodos 'source' y 'target' a las infraestructuras
def asignar_nodos_source_target(cursor):
    try:
        print("Asignando nodos 'source' y 'target' a los segmentos de infraestructura...")
        cursor.execute("SELECT id, ST_AsText(geometry) FROM proyectoalgoritmos.infraestructura")
        infraestructuras = cursor.fetchall()

        for infraestructura in infraestructuras:
            infraestructura_id = infraestructura[0]
            geometry = infraestructura[1]

            # Encontrar el nodo más cercano al punto inicial (source)
            cursor.execute("""
                SELECT id 
                FROM proyectoalgoritmos.infraestructura_nodos 
                ORDER BY ST_Distance(geometry, ST_StartPoint(ST_GeomFromText(%s, 4326))) 
                LIMIT 1;
            """, (geometry,))
            source_result = cursor.fetchone()

            # Encontrar el nodo más cercano al punto final (target)
            cursor.execute("""
                SELECT id 
                FROM proyectoalgoritmos.infraestructura_nodos 
                ORDER BY ST_Distance(geometry, ST_EndPoint(ST_GeomFromText(%s, 4326))) 
                LIMIT 1;
            """, (geometry,))
            target_result = cursor.fetchone()

            # Si ambos nodos existen, actualiza los valores de 'source' y 'target'
            if source_result and target_result:
                source_node = source_result[0]
                target_node = target_result[0]
                cursor.execute("""
                    UPDATE proyectoalgoritmos.infraestructura 
                    SET source = %s, target = %s 
                    WHERE id = %s;
                """, (source_node, target_node, infraestructura_id))

        print("Nodos 'source' y 'target' asignados correctamente.")
    except Exception as e:
        print(f"Error asignando nodos 'source' y 'target': {e}")

# Cargar las variables de entorno desde el archivo .env
print("Cargando variables de entorno...")
load_dotenv(dotenv_path='../.env')

host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

# Conectar a la base de datos
try:
    print(f"Conectando a la base de datos {database}...")
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
    cur = conn.cursor()

    # Procesar ciclovías y calles
    ciclovias = cargar_ciclovias('../Infraestructura/Archivos_descargados/ciclovias_santiago.kml')
    procesar_calles('../Infraestructura/Archivos_descargados/calles_primarias_secundarias_santiago.geojson', ciclovias, cur)

    # Detectar intersecciones
    detectar_intersecciones(cur)

    # Asignar nodos 'source' y 'target'
    asignar_nodos_source_target(cur)

    # Confirmar los cambios
    conn.commit()

except Exception as e:
    print(f"Error durante la ejecución: {e}")

finally:
    # Cerrar la conexión
    cur.close()
    conn.close()
    print("Conexión cerrada y proceso finalizado.")
