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

if len(nodos) < 2:
    print("No se encontraron suficientes nodos para realizar la búsqueda.")
    cur.close()
    conn.close()
    exit()

source = nodos[0][0]
target = nodos[1][0]

cur.execute("SELECT id, ST_AsGeoJSON(geometry) FROM proyectoalgoritmos.infraestructura_nodos WHERE id = %s;", (source,))
source_geom = cur.fetchone()[1]

cur.execute("SELECT id, ST_AsGeoJSON(geometry) FROM proyectoalgoritmos.infraestructura_nodos WHERE id = %s;", (target,))
target_geom = cur.fetchone()[1]

print(f"Source node: {source}, Target node: {target}")

cur.execute("""
    SELECT seq, node, edge, proyectoalgoritmos.infraestructura.cost, 
           ST_AsGeoJSON(proyectoalgoritmos.infraestructura.geometry) AS geometry
    FROM pgr_dijkstra(
        'SELECT id, source, target, cost, 
                CASE WHEN oneway = ''yes'' THEN -1 ELSE cost END AS reverse_cost
         FROM proyectoalgoritmos.infraestructura',
        %s, %s, directed := true
    )
    JOIN proyectoalgoritmos.infraestructura ON proyectoalgoritmos.infraestructura.id = edge;
""", (source, target))

ruta = cur.fetchall()

features = []

if len(ruta) == 0:
    print("No existe una ruta que conecte los nodos seleccionados.")
else:
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

source_feature = {
    "type": "Feature",
    "properties": {
        "node": source,
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
        "node": target,
        "role": "target",
        "marker-color": "#0000ff",
        "marker-symbol": "circle"
    },
    "geometry": json.loads(target_geom)
}
features.append(target_feature)

geojson_result = {
    "type": "FeatureCollection",
    "features": features
}

with open("dijkstra.geojson", "w", encoding="utf-8") as geojson_file:
    json.dump(geojson_result, geojson_file, ensure_ascii=False, indent=4)

print("Resultado exportado como 'dijkstra.geojson'")

cur.close()
conn.close()