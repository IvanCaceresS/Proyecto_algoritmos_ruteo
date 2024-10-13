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

# Seleccionar dos nodos aleatorios que estén en source o target
cur.execute("""
    SELECT id 
    FROM (
        SELECT source AS id FROM proyectoalgoritmos.infraestructura
        UNION
        SELECT target AS id FROM proyectoalgoritmos.infraestructura
    ) AS nodos_validos
    ORDER BY RANDOM()
    LIMIT 2;
""")
nodos = cur.fetchall()
source = nodos[0][0]
target = nodos[1][0]

# Obtener las geometrías de los nodos fijos desde la tabla 'infraestructura_nodos'
cur.execute(f"SELECT id, ST_AsGeoJSON(geometry) FROM proyectoalgoritmos.infraestructura_nodos WHERE id = {source};")
source_geom = cur.fetchone()[1]  # Geometría del nodo de origen

cur.execute(f"SELECT id, ST_AsGeoJSON(geometry) FROM proyectoalgoritmos.infraestructura_nodos WHERE id = {target};")
target_geom = cur.fetchone()[1]  # Geometría del nodo de destino

print(f"Source node: {source}, Target node: {target}")

# Ejecutar pgr_dijkstra para encontrar la ruta más corta entre los nodos usando el campo 'cost'
cur.execute(f"""
    SELECT seq, node, edge, proyectoalgoritmos.infraestructura.cost, 
           ST_AsGeoJSON(proyectoalgoritmos.infraestructura.geometry) AS geometry
    FROM pgr_dijkstra(
        'SELECT id, source, target, proyectoalgoritmos.infraestructura.cost FROM proyectoalgoritmos.infraestructura',
        {source}, {target}, directed := false
    )
    JOIN proyectoalgoritmos.infraestructura ON proyectoalgoritmos.infraestructura.id = edge;
""")

ruta = cur.fetchall()

# Crear una lista vacía para los features
features = []

# Comprobar si la ruta está vacía
if len(ruta) == 0:
    print("No existe una ruta que conecte los nodos seleccionados.")
else:
    # Convertir la ruta en formato GeoJSON
    for row in ruta:
        geometry = row[4]  
        geojson_feature = {
            "type": "Feature",
            "properties": {
                "seq": row[0],
                "node": row[1],
                "edge": row[2],
                "cost": row[3],
                "stroke": "#0000FF",  # Color azul
                "stroke-width": 3     # Ancho de la línea
            },
            "geometry": json.loads(geometry)
        }
        features.append(geojson_feature)

# Agregar el nodo de origen como un punto separado
source_feature = {
    "type": "Feature",
    "properties": {
        "node": source,
        "role": "source",
        "marker-color": "#ff0000",  # Rojo para el origen
        "marker-symbol": "circle"
    },
    "geometry": json.loads(source_geom)
}
features.append(source_feature)

# Agregar el nodo de destino como un punto separado
target_feature = {
    "type": "Feature",
    "properties": {
        "node": target,
        "role": "target",
        "marker-color": "#0000ff",  # Azul para el destino
        "marker-symbol": "circle"
    },
    "geometry": json.loads(target_geom)
}
features.append(target_feature)

# Crear el resultado GeoJSON
geojson_result = {
    "type": "FeatureCollection",
    "features": features
}

# Guardar el resultado en un archivo GeoJSON llamado 'dijkstra.geojson'
with open("dijkstra.geojson", "w", encoding="utf-8") as geojson_file:
    json.dump(geojson_result, geojson_file, ensure_ascii=False, indent=4)

print("Resultado exportado como 'dijkstra.geojson'")

cur.close()
conn.close()
