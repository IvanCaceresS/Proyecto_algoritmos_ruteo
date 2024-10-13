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

# Seleccionar dos nodos aleatorios de la tabla 'infraestructura_nodos'
cur.execute("SELECT id, ST_AsGeoJSON(geometry) FROM infraestructura_nodos ORDER BY RANDOM() LIMIT 2;")
nodos = cur.fetchall()
source = nodos[0][0]
target = nodos[1][0]
source_geom = nodos[0][1]  # Geometría del nodo de origen
target_geom = nodos[1][1]  # Geometría del nodo de destino

print(f"Source node: {source}, Target node: {target}")

# Ejecutar pgr_dijkstra para encontrar la ruta más corta entre los nodos
cur.execute(f"""
    SELECT seq, node, edge, cost, ST_AsGeoJSON(infraestructura.geometry) AS geometry
    FROM pgr_dijkstra(
        'SELECT id, source, target, ST_Length(geometry) AS cost FROM infraestructura',
        {source}, {target}, directed := false
    )
    JOIN infraestructura ON infraestructura.id = edge;
""")

ruta = cur.fetchall()

# Comprobar si la ruta está vacía
features = []
if len(ruta) == 0:
    geojson_result = {
        "type": "FeatureCollection",
        "features": [],
        "message": "No existe una ruta que conecte los nodos seleccionados."
    }
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
                "cost": row[3]
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
