import os
import psycopg2
import json
import pandas as pd
import sys
from dotenv import load_dotenv
from calculo_resiliencia import calcular_resiliencia
import networkx as nx
import random

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
fallas_infra_cierre = fallas_df[(fallas_df['amenaza'] == 'cierre_calle') & fallas_df['id_infraestructura'].notna()]['id_infraestructura'].astype(int).tolist()

print(f"Calculando ruta desde el nodo {source_id} hasta el nodo {target_id}")

# Construir el grafo usando NetworkX
G = nx.DiGraph()
cur.execute("SELECT id, source, target, cost, ST_AsGeoJSON(geometry) FROM proyectoalgoritmos.infraestructura")
edges = cur.fetchall()
for edge in edges:
    edge_id, u, v, cost, geometry = edge
    if edge_id in fallas_infra_cierre:
        continue  # Ignorar los bordes afectados por cierre de calle
    G.add_edge(u, v, id=edge_id, cost=cost, geometry=json.loads(geometry))

# Parámetros de ACO
NUM_HORMIGAS = 100  # Incrementado para más exploración
ITERACIONES = 200  # Incrementado para más exploración
EVAPORACION = 0.4
INTENSIDAD_FEROMONA = 100
ALPHA = 1  # Peso de la feromona
BETA = 2.5  # Peso de la heurística incrementado

# Inicializar feromonas
for u, v in G.edges():
    G[u][v]["feromona"] = 1.0  # Nivel inicial de feromona

def elegir_siguiente_nodo(G, nodo_actual, destino, no_visitados):
    """Función para que una hormiga elija el siguiente nodo basado en feromonas y heurística"""
    edges = list(G.edges(nodo_actual, data=True))
    pesos = []
    for _, siguiente, data in edges:
        if siguiente in no_visitados:
            feromona = data["feromona"] ** ALPHA
            heuristica = (1 / data["cost"]) ** BETA
            pesos.append(feromona * heuristica)
        else:
            pesos.append(0)
    if sum(pesos) == 0:
        return None
    return random.choices([edge[1] for edge in edges], weights=pesos, k=1)[0]

def colonia_hormigas(G, origen, destino):
    """Algoritmo de colonia de hormigas para encontrar una ruta óptima en el grafo"""
    mejor_ruta = None
    mejor_costo = float('inf')

    for _ in range(ITERACIONES):
        rutas = []
        costos = []
        for _ in range(NUM_HORMIGAS):
            nodo_actual = origen
            no_visitados = set(G.nodes)
            ruta = [nodo_actual]
            costo_total = 0
            no_visitados.remove(nodo_actual)

            while nodo_actual != destino:
                siguiente_nodo = elegir_siguiente_nodo(G, nodo_actual, destino, no_visitados)
                if siguiente_nodo is None:
                    break
                costo_total += G[nodo_actual][siguiente_nodo]["cost"]
                ruta.append(siguiente_nodo)
                no_visitados.remove(siguiente_nodo)
                nodo_actual = siguiente_nodo

            if nodo_actual == destino:
                rutas.append(ruta)
                costos.append(costo_total)
                if costo_total < mejor_costo:
                    mejor_ruta = ruta
                    mejor_costo = costo_total

        # Evaporar feromonas
        for u, v in G.edges():
            G[u][v]["feromona"] *= (1 - EVAPORACION)
        for ruta, costo in zip(rutas, costos):
            for i in range(len(ruta) - 1):
                u, v = ruta[i], ruta[i + 1]
                G[u][v]["feromona"] += INTENSIDAD_FEROMONA / costo

    return mejor_ruta, mejor_costo

# Ejecutar ACO
mejor_ruta, mejor_costo = colonia_hormigas(G, source_id, target_id)

# Verificar si se encontró una ruta válida
if mejor_ruta is None or len(mejor_ruta) < 2:
    print("Error: No se encontró una ruta válida con el algoritmo ACO.")
    cur.close()
    conn.close()
    sys.exit(1)

print("Mejor ruta:", mejor_ruta)
print("Costo de la mejor ruta:", mejor_costo)

# Preparar datos para calcular la resiliencia
ruta_data = [(G[u][v]["id"], G[u][v]["cost"]) for u, v in zip(mejor_ruta[:-1], mejor_ruta[1:])]
fallas_infra = fallas_infra_cierre  # Considera las infraestructuras afectadas

# Calcular resiliencia
resiliencia = calcular_resiliencia(ruta_data, fallas_infra)
resiliencia_costo = resiliencia["resiliencia_costo"]
resiliencia_impacto = resiliencia["resiliencia_impacto"]

# Generar GeoJSON
features = []
for u, v in zip(mejor_ruta[:-1], mejor_ruta[1:]):
    afectado = G[u][v]["id"] in fallas_infra
    geojson_feature = {
        "type": "Feature",
        "properties": {
            "source": u,
            "target": v,
            "id": G[u][v]["id"],
            "cost": G[u][v]["cost"],
            "afectado": "Sí" if afectado else "No",
            "stroke": "#FF0000" if afectado else "#0000FF",
            "stroke-width": 3
        },
        "geometry": G[u][v]["geometry"]
    }
    features.append(geojson_feature)

geojson_result = {
    "type": "FeatureCollection",
    "features": features
}

geojson_path = "./static/aco_route.geojson"
with open(geojson_path, "w", encoding="utf-8") as geojson_file:
    json.dump(geojson_result, geojson_file, ensure_ascii=False, indent=4)
print(f"Resultado exportado como '{geojson_path}'")

# Exportar las métricas de resiliencia
resiliencia_path = "./static/aco_resiliencia.txt"
with open(resiliencia_path, "w", encoding="utf-8") as txt_file:
    txt_file.write("Métricas de resiliencia de la ruta frente a amenazas:\n")
    txt_file.write(f" - Resiliencia en costo (relativa): {resiliencia_costo:.2f}\n")
    txt_file.write(f" - Resiliencia en impacto (elementos no afectados): {resiliencia_impacto:.2f}\n")

print(f"Métricas de resiliencia exportadas como '{resiliencia_path}'")

# Cerrar la conexión a la base de datos
cur.close()
conn.close()
