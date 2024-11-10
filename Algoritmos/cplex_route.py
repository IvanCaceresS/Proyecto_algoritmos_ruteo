import os
import json
import psycopg2
from docplex.mp.model import Model
from dotenv import load_dotenv
import pandas as pd
import sys
from calculo_resiliencia import calcular_resiliencia

load_dotenv(dotenv_path='../.env')

# Configurar la ruta de CPLEX en la variable de entorno
os.environ['CPLEX_STUDIO_DIR2211'] = "C:\\Program Files\\IBM\\ILOG\\CPLEX_Studio2211"

# Configuración de conexión a la base de datos
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
conn = psycopg2.connect(host=host, database=database, user=user, password=password)
cur = conn.cursor()

# Obtener los IDs de los nodos de inicio y fin desde los argumentos
source_id = int(sys.argv[1])
target_id = int(sys.argv[2])

# Cargar los datos de amenazas activas
fallas_df = pd.read_csv('./static/Fallas/amenazas_ocurriendo.csv')

# Filtrar IDs para cada tipo de amenaza
fallas_infra_cierre = fallas_df[(fallas_df['amenaza'] == 'cierre_calle') & fallas_df['id_infraestructura'].notna()]['id_infraestructura'].astype(int).tolist()
fallas_infra_seguridad = fallas_df[(fallas_df['amenaza'] == 'seguridad') & fallas_df['id_infraestructura'].notna()]['id_infraestructura'].astype(int).tolist()
fallas_infra_trafico = fallas_df[(fallas_df['amenaza'] == 'trafico') & fallas_df['id_infraestructura'].notna()]['id_infraestructura'].astype(int).tolist()
fallas_infra_precipitacion = fallas_df[(fallas_df['amenaza'] == 'precipitacion_inundacion') & fallas_df['id_infraestructura'].notna()]['id_infraestructura'].astype(int).tolist()

# Crear condiciones ajustadas para cada amenaza si las listas no están vacías
conditions = []
if fallas_infra_seguridad:
    conditions.append(f"WHEN i.id IN ({', '.join(map(str, fallas_infra_seguridad))}) THEN i.cost * 1.5")
if fallas_infra_trafico:
    conditions.append(f"WHEN i.id IN ({', '.join(map(str, fallas_infra_trafico))}) THEN i.cost * 1.2")
if fallas_infra_precipitacion:
    conditions.append(f"WHEN i.id IN ({', '.join(map(str, fallas_infra_precipitacion))}) THEN i.cost * 1.1")

# Construir el CASE con condiciones o un valor predeterminado si están vacías
adjusted_cost_case = "CASE " + " ".join(conditions) + " ELSE i.cost END AS adjusted_cost"

# Condición para excluir calles cerradas, o "TRUE" si la lista está vacía
infra_cierre_cond = f"i.id NOT IN ({', '.join(map(str, fallas_infra_cierre))})" if fallas_infra_cierre else "TRUE"

# Consulta para obtener la infraestructura con los costos ajustados
cur.execute(f"""
    SELECT i.id, i.source, i.target,
           {adjusted_cost_case},
           i.is_ciclovia
    FROM proyectoalgoritmos.infraestructura AS i
    LEFT JOIN proyectoalgoritmos.velocidades_maximas AS v ON i.id = v.geojson_id::BIGINT
    LEFT JOIN proyectoalgoritmos.estacionamientos AS e ON i.id = REGEXP_REPLACE(e.geojson_id, '^node/', '')::BIGINT
    LEFT JOIN proyectoalgoritmos.iluminacion AS il ON i.id = il.geojson_id
    LEFT JOIN proyectoalgoritmos.inundaciones AS inf ON ST_Intersects(i.geometry, inf.geometry)
    WHERE {infra_cierre_cond};
""")

# Guardar los resultados de la consulta en un diccionario para la optimización
edges = {}
for row in cur.fetchall():
    edge_id, source, target, adjusted_cost, is_ciclovia = row
    edges[edge_id] = {
        "source": source,
        "target": target,
        "adjusted_cost": adjusted_cost,
        "is_ciclovia": is_ciclovia
    }

# Configurar el modelo de optimización
mdl = Model(name="ruta_optima")
edge_vars = {e: mdl.binary_var(name=f"edge_{e}") for e in edges}

# Definir la función objetivo
mdl.minimize(mdl.sum(edge_vars[e] * edges[e]["adjusted_cost"] for e in edges))

# Restricciones de flujo de entrada y salida en los nodos de inicio y fin
for node in set(edge["source"] for edge in edges.values()).union(edge["target"] for edge in edges.values()):
    incoming = [e for e in edges if edges[e]["target"] == node]
    outgoing = [e for e in edges if edges[e]["source"] == node]
    
    if node == source_id:
        mdl.add_constraint(mdl.sum(edge_vars[e] for e in outgoing) - mdl.sum(edge_vars[e] for e in incoming) == 1)
    elif node == target_id:
        mdl.add_constraint(mdl.sum(edge_vars[e] for e in incoming) - mdl.sum(edge_vars[e] for e in outgoing) == 1)
    else:
        mdl.add_constraint(mdl.sum(edge_vars[e] for e in incoming) == mdl.sum(edge_vars[e] for e in outgoing))

# Resolver el modelo
solution = mdl.solve()

# Verificar si se encontró una solución
if solution:
    print("Solución encontrada.")
    route_edges = [e for e in edges if edge_vars[e].solution_value > 0.5]

    # Preparar los datos de la ruta para el cálculo de resiliencia
    ruta = [(edge_id, edges[edge_id]["adjusted_cost"]) for edge_id in route_edges]

    # Calcular resiliencia usando la función importada
    fallas_infra = fallas_infra_seguridad + fallas_infra_trafico + fallas_infra_precipitacion
    resiliencia = calcular_resiliencia(ruta, fallas_infra)

    # Extraer métricas de resiliencia
    resiliencia_costo = resiliencia["resiliencia_costo"]
    resiliencia_impacto = resiliencia["resiliencia_impacto"]
    elementos_afectados = resiliencia["elementos_afectados"]

    # Exportar las métricas de resiliencia a un archivo de texto
    resiliencia_path = "./static/cplex_resiliencia.txt"
    if os.path.exists(resiliencia_path):
        os.remove(resiliencia_path)

    with open(resiliencia_path, "w", encoding="utf-8") as txt_file:
        txt_file.write("Métricas de resiliencia de la ruta frente a amenazas:\n")
        txt_file.write(f" - Resiliencia en costo (relativa): {resiliencia_costo:.2f}\n")
        txt_file.write(f" - Resiliencia en impacto (elementos no afectados): {resiliencia_impacto:.2f}\n")

    print(f"Métricas de resiliencia exportadas como '{resiliencia_path}'")

    # Exportar la ruta a un archivo GeoJSON
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
    if os.path.exists(geojson_path):
        os.remove(geojson_path)

    with open(geojson_path, "w", encoding="utf-8") as geojson_file:
        json.dump(geojson_result, geojson_file, ensure_ascii=False, indent=4)

    print("Resultado exportado como 'cplex_route.geojson'")
else:
    print("No se encontró una solución óptima.")
    # Salida sin datos
    with open("./static/cplex_route.geojson", "w", encoding="utf-8") as f:
        f.write('{"type": "FeatureCollection", "features": []}')

cur.close()
conn.close()
