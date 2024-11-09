import os
import json
import psycopg2
from docplex.mp.model import Model
from dotenv import load_dotenv
import sys

load_dotenv(dotenv_path='../.env')

# Configurar la ruta de CPLEX en la variable de entorno
os.environ['CPLEX_STUDIO_DIR2211'] = "C:\\Program Files\\IBM\\ILOG\\CPLEX_Studio2211"

host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
conn = psycopg2.connect(host=host, database=database, user=user, password=password)
cur = conn.cursor()

source_id = int(sys.argv[1])
target_id = int(sys.argv[2])

mdl = Model(name="ruta_optima")

cur.execute("""
    SELECT i.id, i.source, i.target,
           CASE 
               WHEN inf.ind_riesgo_inundaciones_t10_delta > 5 THEN i.cost * 2
               WHEN v.maxspeed::float < 20 THEN i.cost * 1.5
               WHEN e.capacity IS NOT NULL AND e.capacity > 0 THEN i.cost * 0.8
               WHEN il.lit = 'yes' THEN i.cost * 0.9
               ELSE i.cost
           END AS adjusted_cost,
           i.is_ciclovia
    FROM proyectoalgoritmos.infraestructura AS i
    LEFT JOIN proyectoalgoritmos.velocidades_maximas AS v ON i.id = v.geojson_id::BIGINT
    LEFT JOIN proyectoalgoritmos.estacionamientos AS e ON i.id = REGEXP_REPLACE(e.geojson_id, '^node/', '')::BIGINT
    LEFT JOIN proyectoalgoritmos.iluminacion AS il ON i.id = il.geojson_id
    LEFT JOIN proyectoalgoritmos.inundaciones AS inf ON ST_Intersects(i.geometry, inf.geometry);
""")

edges = {}
for row in cur.fetchall():
    edge_id, source, target, adjusted_cost, is_ciclovia = row
    edges[edge_id] = {
        "source": source,
        "target": target,
        "adjusted_cost": adjusted_cost,
        "is_ciclovia": is_ciclovia
    }

edge_vars = {e: mdl.binary_var(name=f"edge_{e}") for e in edges}

mdl.minimize(mdl.sum(edge_vars[e] * edges[e]["adjusted_cost"] for e in edges))

for node in set(edge["source"] for edge in edges.values()).union(edge["target"] for edge in edges.values()):
    incoming = [e for e in edges if edges[e]["target"] == node]
    outgoing = [e for e in edges if edges[e]["source"] == node]
    
    if node == source_id:
        mdl.add_constraint(mdl.sum(edge_vars[e] for e in outgoing) - mdl.sum(edge_vars[e] for e in incoming) == 1)
    elif node == target_id:
        mdl.add_constraint(mdl.sum(edge_vars[e] for e in incoming) - mdl.sum(edge_vars[e] for e in outgoing) == 1)
    else:
        mdl.add_constraint(mdl.sum(edge_vars[e] for e in incoming) == mdl.sum(edge_vars[e] for e in outgoing))

solution = mdl.solve()

if solution:
    print("Solución encontrada.")
    route_edges = [e for e in edges if edge_vars[e].solution_value > 0.5]

    features = []
    for edge_id in route_edges:
        cur.execute("""
            SELECT id, ST_AsGeoJSON(geometry) AS geometry
            FROM proyectoalgoritmos.infraestructura
            WHERE id = %s
        """, (edge_id,))
        result = cur.fetchone()
        if result:
            feature = {
                "type": "Feature",
                "properties": {"id": result[0]},
                "geometry": json.loads(result[1])
            }
            features.append(feature)

    geojson_result = {
        "type": "FeatureCollection",
        "features": features
    }

    geojson_path = "./static/cplex_route.geojson"
    with open(geojson_path, "w", encoding="utf-8") as geojson_file:
        json.dump(geojson_result, geojson_file, ensure_ascii=False, indent=4)

    print("Resultado exportado como 'cplex_route.geojson'")
else:
    print("No se encontró una solución óptima.")

cur.close()
conn.close()
