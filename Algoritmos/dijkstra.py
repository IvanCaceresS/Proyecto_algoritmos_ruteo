import os
import psycopg2
import json
import pandas as pd
import sys
from dotenv import load_dotenv
from calculo_resiliencia import calcular_resiliencia  # Importar la función de cálculo de resiliencia

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
fallas_infra = fallas_df['id_infraestructura'].dropna().astype(int).tolist()

print(f"Calculando ruta desde el nodo {source_id} hasta el nodo {target_id}")

# Ejecutar el algoritmo de Dijkstra para calcular la ruta entre source_id y target_id
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
""", (source_id, target_id))

# Obtener los resultados de la ruta
ruta = cur.fetchall()
print("Ruta encontrada con", len(ruta), "elementos.")

# Preparar los datos de la ruta para el cálculo de resiliencia
ruta_data = [(row[2], row[3]) for row in ruta]  # [(edge_id, cost)]

# Calcular resiliencia usando la función importada
resiliencia = calcular_resiliencia(ruta_data, fallas_infra)

# Extraer métricas de resiliencia
resiliencia_costo = resiliencia["resiliencia_costo"]
resiliencia_impacto = resiliencia["resiliencia_impacto"]
elementos_afectados = resiliencia["elementos_afectados"]

# Crear la estructura de GeoJSON para exportar la ruta
features = []
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

geojson_path = "./static/dijkstra.geojson"
with open(geojson_path, "w", encoding="utf-8") as geojson_file:
    json.dump(geojson_result, geojson_file, ensure_ascii=False, indent=4)
print(f"Resultado exportado como '{geojson_path}'")

# Exportar las métricas de resiliencia a un archivo de texto
resiliencia_path = "./static/dijkstra_resiliencia.txt"
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
