import os
import psycopg2
import json
import pandas as pd
import sys
from dotenv import load_dotenv
from calculo_resiliencia import calcular_resiliencia

# Cargar las variables de entorno
load_dotenv(dotenv_path='../.env')

# Verificar que se pasaron los argumentos necesarios
print("Argumentos recibidos:", sys.argv)
if len(sys.argv) < 3:
    print("Se requieren los IDs de los nodos de inicio y fin.")
    sys.exit(1)

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

# Cargar los datos de amenazas activas
fallas_df = pd.read_csv('./static/Fallas/amenazas_ocurriendo.csv')

# Filtrar IDs para "cierre de calle" (exclusión total) y otras amenazas (incremento de peso)
fallas_infra_cierre = fallas_df[(fallas_df['amenaza'] == 'cierre_calle') & fallas_df['id_infraestructura'].notna()]['id_infraestructura'].astype(int).tolist()
fallas_nodos_cierre = fallas_df[(fallas_df['amenaza'] == 'cierre_calle') & fallas_df['id_nodo'].notna()]['id_nodo'].astype(int).tolist()

# Filtrar IDs para las demás amenazas
fallas_infra_seguridad = fallas_df[(fallas_df['amenaza'] == 'seguridad') & fallas_df['id_infraestructura'].notna()]['id_infraestructura'].astype(int).tolist()
fallas_infra_trafico = fallas_df[(fallas_df['amenaza'] == 'trafico') & fallas_df['id_infraestructura'].notna()]['id_infraestructura'].astype(int).tolist()
fallas_infra_precipitacion = fallas_df[(fallas_df['amenaza'] == 'precipitacion_inundacion') & fallas_df['id_infraestructura'].notna()]['id_infraestructura'].astype(int).tolist()

print(f"Calculando ruta desde el nodo {source_id} hasta el nodo {target_id}")

# Construir condiciones condicionales para exclusión de cierres de calle
infra_cierre_cond = f"i.id NOT IN ({', '.join(map(str, fallas_infra_cierre))})" if fallas_infra_cierre else "TRUE"
nodos_cierre_cond = f"i.source NOT IN ({', '.join(map(str, fallas_nodos_cierre))}) AND i.target NOT IN ({', '.join(map(str, fallas_nodos_cierre))})" if fallas_nodos_cierre else "TRUE"

# Ajustar costos solo si existen IDs en las listas correspondientes
adjusted_cost_conditions = []
if fallas_infra_seguridad:
    adjusted_cost_conditions.append(f"WHEN i.id IN ({', '.join(map(str, fallas_infra_seguridad))}) THEN i.cost * 1.5")
if fallas_infra_trafico:
    adjusted_cost_conditions.append(f"WHEN i.id IN ({', '.join(map(str, fallas_infra_trafico))}) THEN i.cost * 1.2")
if fallas_infra_precipitacion:
    adjusted_cost_conditions.append(f"WHEN i.id IN ({', '.join(map(str, fallas_infra_precipitacion))}) THEN i.cost * 1.1")

# Crear la consulta de CASE para adjusted_cost
adjusted_cost_case = "CASE " + " ".join(adjusted_cost_conditions) + " ELSE i.cost END AS adjusted_cost"

# Crear una vista temporal ajustada que tenga en cuenta amenazas activas y metadatos
cur.execute(f"""
    CREATE OR REPLACE VIEW proyectoalgoritmos.infraestructura_ajustada AS
    SELECT 
        i.id,
        i.source,
        i.target,
        i.oneway,
        {adjusted_cost_case},
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
        ON ST_Intersects(i.geometry, inf.geometry)
    WHERE {infra_cierre_cond} AND {nodos_cierre_cond};
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

# Preparar los datos de la ruta para el cálculo de resiliencia
ruta_data = [(row[2], row[3]) for row in ruta]  # [(edge_id, cost)]

# Calcular resiliencia usando la función importada
fallas_infra = fallas_infra_seguridad + fallas_infra_trafico + fallas_infra_precipitacion
resiliencia = calcular_resiliencia(ruta_data, fallas_infra)

# Extraer métricas de resiliencia
resiliencia_costo = resiliencia["resiliencia_costo"]
resiliencia_impacto = resiliencia["resiliencia_impacto"]
elementos_afectados = resiliencia["elementos_afectados"]

# Crear la estructura de GeoJSON
features = []

if len(ruta) == 0:
    print("No existe una ruta que conecte los nodos seleccionados.")
    cur.close()
    conn.close()
    with open("./static/dijkstra_complete.geojson", "w") as f:
        f.write('{"type": "FeatureCollection", "features": []}')
    sys.exit(0)

# Continuar si se encontró la ruta
for row in ruta:
    geometry = row[4]
    afectado = row[2] in fallas_infra
    geojson_feature = {
        "type": "Feature",
        "properties": {
            "seq": row[0],
            "node": row[1],
            "edge": row[2],
            "cost": row[3],
            "afectado": "Sí" if afectado else "No",
            "stroke": "#FF0000" if afectado else "#0000FF",
            "stroke-width": 3
        },
        "geometry": json.loads(geometry)
    }
    features.append(geojson_feature)

# Exportar la ruta con los detalles de resiliencia
geojson_result = {
    "type": "FeatureCollection",
    "features": features
}

geojson_path = "./static/dijkstra_complete.geojson"
if os.path.exists(geojson_path):
    os.remove(geojson_path)

with open(geojson_path, "w", encoding="utf-8") as geojson_file:
    json.dump(geojson_result, geojson_file, ensure_ascii=False, indent=4)
print(f"Resultado exportado como '{geojson_path}'")

# Exportar las métricas de resiliencia a un archivo de texto
resiliencia_path = "./static/dijkstra_complete_resiliencia.txt"
if os.path.exists(resiliencia_path):
    os.remove(resiliencia_path)

with open(resiliencia_path, "w", encoding="utf-8") as txt_file:
    txt_file.write("Métricas de resiliencia de la ruta frente a amenazas:\n")
    txt_file.write(f" - Resiliencia en costo (relativa): {resiliencia_costo:.2f}\n")
    txt_file.write(f" - Resiliencia en impacto (elementos no afectados): {resiliencia_impacto:.2f}\n")

print(f"Métricas de resiliencia exportadas como '{resiliencia_path}'")

# Cerrar el cursor y la conexión a la base de datos
cur.close()
conn.close()
