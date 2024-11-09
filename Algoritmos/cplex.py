import os
import json
import psycopg2
from docplex.mp.model import Model
from dotenv import load_dotenv
import sys

# Cargar variables de entorno
load_dotenv(dotenv_path='../.env')

# Conectar a la base de datos
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
conn = psycopg2.connect(host=host, database=database, user=user, password=password)
cur = conn.cursor()

# Obtener los IDs de los nodos de inicio y fin desde los argumentos
source_id = int(sys.argv[1])
target_id = int(sys.argv[2])

# 1. Configurar el modelo de optimización
mdl = Model(name="ruta_optima")

# 2. Consultar la información de los tramos de infraestructura (enlaces) y metadatos
cur.execute("""
    SELECT i.id, i.source, i.target, i.cost, i.is_ciclovia, 
           COALESCE(v.maxspeed::float, 50) AS maxspeed,
           CASE WHEN e.capacity > 0 THEN 1 ELSE 0 END AS estacionamiento,
           CASE WHEN il.lit = 'yes' THEN 1 ELSE 0 END AS iluminado,
           COALESCE(inf.ind_riesgo_inundaciones_t10_delta, 0) AS riesgo_inundacion
    FROM proyectoalgoritmos.infraestructura AS i
    LEFT JOIN proyectoalgoritmos.velocidades_maximas AS v ON i.id = v.geojson_id
    LEFT JOIN proyectoalgoritmos.estacionamientos AS e ON i.id = e.geojson_id
    LEFT JOIN proyectoalgoritmos.iluminacion AS il ON i.id = il.geojson_id
    LEFT JOIN proyectoalgoritmos.inundaciones AS inf ON ST_Intersects(i.geometry, inf.geometry);
""")

# Crear diccionarios para almacenar los datos de los enlaces
edges = {}
for row in cur.fetchall():
    edge_id, source, target, cost, is_ciclovia, maxspeed, estacionamiento, iluminado, riesgo_inundacion = row
    edges[edge_id] = {
        "source": source,
        "target": target,
        "cost": cost,
        "is_ciclovia": is_ciclovia,
        "maxspeed": maxspeed,
        "estacionamiento": estacionamiento,
        "iluminado": iluminado,
        "riesgo_inundacion": riesgo_inundacion
    }

# 3. Variables de decisión para cada enlace (1 si se usa el enlace en la ruta, 0 si no)
edge_vars = {e: mdl.binary_var(name=f"edge_{e}") for e in edges}

# 4. Función objetivo: Minimizar el costo total de la ruta
mdl.minimize(mdl.sum(edge_vars[e] * edges[e]["cost"] for e in edges))

# 5. Restricciones:
#   a. Flujo de entrada y salida en los nodos
for e in edges:
    source = edges[e]["source"]
    target = edges[e]["target"]
    if source == source_id:
        mdl.add_constraint(edge_vars[e] == 1, f"source_{source}")
    elif target == target_id:
        mdl.add_constraint(edge_vars[e] == 1, f"target_{target}")

#   b. Asegurar que el flujo sea continuo de origen a destino
for node in set(edge["source"] for edge in edges.values()).union(edge["target"] for edge in edges.values()):
    incoming = [e for e in edges if edges[e]["target"] == node]
    outgoing = [e for e in edges if edges[e]["source"] == node]
    if node != source_id and node != target_id:
        mdl.add_constraint(mdl.sum(edge_vars[e] for e in incoming) == mdl.sum(edge_vars[e] for e in outgoing))

#   c. Restricciones basadas en amenazas y condiciones del usuario
# Ejemplo de restricciones en base a los metadatos y amenazas
for e in edges:
    # Evitar tramos con riesgo alto de inundación
    if edges[e]["riesgo_inundacion"] > 5:
        mdl.add_constraint(edge_vars[e] == 0, f"no_high_inundacion_{e}")
    
    # Priorizar iluminación en el camino
    if edges[e]["iluminado"] == 0:
        mdl.add_constraint(edge_vars[e] == 0, f"must_be_iluminado_{e}")
    
    # Evitar tramos sin estacionamiento si el usuario lo solicita
    if edges[e]["estacionamiento"] == 0:
        mdl.add_constraint(edge_vars[e] == 0, f"must_have_estacionamiento_{e}")
    
    # Limitar la velocidad máxima en ciertos segmentos
    if edges[e]["maxspeed"] < 20:
        mdl.add_constraint(edge_vars[e] == 0, f"min_speed_{e}")

# 6. Resolver el modelo
solution = mdl.solve()

if solution:
    print("Solución encontrada.")
    # Extraer la ruta y formatearla en GeoJSON
    route_edges = [e for e in edges if edge_vars[e].solution_value > 0.5]

    # Consulta para obtener la geometría de los tramos seleccionados
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

    # Crear el GeoJSON
    geojson_result = {
        "type": "FeatureCollection",
        "features": features
    }

    # Guardar el resultado en un archivo GeoJSON
    geojson_path = "./static/cplex_route.geojson"
    with open(geojson_path, "w", encoding="utf-8") as geojson_file:
        json.dump(geojson_result, geojson_file, ensure_ascii=False, indent=4)

    print("Resultado exportado como 'cplex_route.geojson'")
else:
    print("No se encontró una solución óptima.")

# Cerrar la conexión a la base de datos
cur.close()
conn.close()
