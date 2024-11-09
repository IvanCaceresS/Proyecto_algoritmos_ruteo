import psycopg2
import json
import sys
from dotenv import load_dotenv
import os

# Mensaje de depuración para ver los argumentos recibidos
print("Argumentos recibidos:", sys.argv)

# Verificar que se pasaron los argumentos necesarios
if len(sys.argv) < 3:
    print("Se requieren los IDs de los nodos de inicio y fin.")
    sys.exit(1)

# Cargar las variables de entorno
load_dotenv(dotenv_path='../.env')

# Conectar a la base de datos con las credenciales del archivo de entorno
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

# Obtener los IDs de los nodos de inicio y fin desde los argumentos
source_id = int(sys.argv[1])
target_id = int(sys.argv[2])

# Establecer la conexión a la base de datos
conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password
)
cur = conn.cursor()

print(f"Calculando ruta desde el nodo {source_id} hasta el nodo {target_id}")

# Crear una vista temporal ajustada para aplicar las condiciones de amenazas y metadatos
cur.execute("""
    CREATE OR REPLACE VIEW proyectoalgoritmos.infraestructura_ajustada AS
    SELECT 
        i.id,
        i.source,
        i.target,
        i.oneway,  -- Incluir la columna 'oneway' en la vista
        CASE 
            WHEN inf.ind_riesgo_inundaciones_t10_delta > 5 THEN i.cost * 2 -- Duplicar el costo en caso de alto riesgo de inundación
            WHEN v.maxspeed::float < 20 THEN i.cost * 1.5 -- Incrementar el costo para caminos con baja velocidad máxima
            WHEN e.capacity IS NOT NULL AND e.capacity > 0 THEN i.cost * 0.8 -- Reducir el costo si hay estacionamiento disponible
            WHEN il.lit = 'yes' THEN i.cost * 0.9 -- Reducir ligeramente el costo en áreas iluminadas
            ELSE i.cost
        END AS adjusted_cost,
        i.geometry
    FROM 
        proyectoalgoritmos.infraestructura AS i
    LEFT JOIN proyectoalgoritmos.velocidades_maximas AS v 
        ON i.id = v.geojson_id::BIGINT
    LEFT JOIN proyectoalgoritmos.estacionamientos AS e 
        ON i.id = REGEXP_REPLACE(e.geojson_id, '^node/', '')::BIGINT
    LEFT JOIN proyectoalgoritmos.iluminacion AS il 
        ON i.id = il.geojson_id
    LEFT JOIN proyectoalgoritmos.inundaciones AS inf 
        ON ST_Intersects(i.geometry, inf.geometry);
""")

# Ejecutar `pgr_dijkstra` utilizando la vista con costos ajustados
cur.execute("""
    SELECT 
        seq, node, edge, cost, 
        ST_AsGeoJSON(i.geometry) AS geometry
    FROM 
        pgr_dijkstra(
            'SELECT id, source, target, adjusted_cost AS cost, 
                    CASE WHEN oneway = ''yes'' THEN -1 ELSE adjusted_cost END AS reverse_cost
             FROM proyectoalgoritmos.infraestructura_ajustada',
            %s, %s, directed := true
        ) AS dij
    JOIN proyectoalgoritmos.infraestructura_ajustada AS i ON dij.edge = i.id;
""", (source_id, target_id))

# Obtener los resultados de la ruta
ruta = cur.fetchall()
print("Ruta encontrada con", len(ruta), "elementos.")

# Crear la estructura de GeoJSON
features = []

if len(ruta) == 0:
    print("No existe una ruta que conecte los nodos seleccionados.")
    # Cerrar el cursor y la conexión
    cur.close()
    conn.close()
    # Salida especial para indicar que no se encontró la ruta
    with open("./static/dijkstra_complete.geojson", "w") as f:
        json.dump({"error": "No se encontró una ruta entre los nodos especificados."}, f)
    sys.exit(0)  # Finaliza el script correctamente pero con un mensaje de error

# Continuar si se encontró la ruta
for row in ruta:
    geometry = row[4]  
    geojson_feature = {
        "type": "Feature",
        "properties": {
            "seq": row[0],
            "node": row[1],
            "edge": row[2],
            "cost": row[3],
            "stroke": "#0000FF",
            "stroke-width": 3
        },
        "geometry": json.loads(geometry)
    }
    features.append(geojson_feature)

# Obtener las geometrías de los nodos de inicio y fin para agregarlas al resultado GeoJSON
cur.execute("SELECT id, ST_AsGeoJSON(geometry) FROM proyectoalgoritmos.infraestructura_nodos WHERE id = %s;", (source_id,))
source_geom = cur.fetchone()[1]

cur.execute("SELECT id, ST_AsGeoJSON(geometry) FROM proyectoalgoritmos.infraestructura_nodos WHERE id = %s;", (target_id,))
target_geom = cur.fetchone()[1]

# Agregar los puntos de inicio y fin al GeoJSON
source_feature = {
    "type": "Feature",
    "properties": {
        "node": source_id,
        "role": "source",
        "marker-color": "#ff0000",
        "marker-symbol": "circle"
    },
    "geometry": json.loads(source_geom)
}
features.append(source_feature)

target_feature = {
    "type": "Feature",
    "properties": {
        "node": target_id,
        "role": "target",
        "marker-color": "#0000ff",
        "marker-symbol": "circle"
    },
    "geometry": json.loads(target_geom)
}
features.append(target_feature)

# Crear el objeto GeoJSON final
geojson_result = {
    "type": "FeatureCollection",
    "features": features
}

# Definir la ruta donde se guardará el archivo GeoJSON
geojson_path = "./static/dijkstra_complete.geojson"

# Eliminar el archivo GeoJSON previo si existe
if os.path.exists(geojson_path):
    os.remove(geojson_path)

# Guardar el resultado como un archivo GeoJSON
with open(geojson_path, "w", encoding="utf-8") as geojson_file:
    json.dump(geojson_result, geojson_file, ensure_ascii=False, indent=4)

print("Resultado exportado como 'dijkstra_complete.geojson'")

# Cerrar el cursor y la conexión a la base de datos
cur.close()
conn.close()
