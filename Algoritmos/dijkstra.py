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

# Crear diccionario de tipos de amenazas por infraestructura
tipos_amenazas = dict(zip(fallas_df['id_infraestructura'].dropna().astype(int), fallas_df['amenaza']))

# Definir los multiplicadores para cada tipo de amenaza
multiplicadores_amenazas = {
    'cierre_calle': 3,
    'seguridad': 2,
    'trafico': 1.5,
    'precipitacion_inundacion': 2.5
}

# Filtrar solo los IDs de infraestructuras afectadas
fallas_infra = list(tipos_amenazas.keys())

print(f"Calculando ruta desde el nodo {source_id} hasta el nodo {target_id}")

# Ejecutar el algoritmo de Dijkstra para calcular la ruta entre source_id y target_id
cur.execute("""
    SELECT dij.seq, dij.node, dij.edge, dij.cost,
           ST_AsGeoJSON(infra.geometry) AS geometry
    FROM pgr_dijkstra(
        'SELECT id, source, target, 
                ST_Length(geometry::geography) AS cost, 
                CASE 
                    WHEN oneway = ''yes'' THEN -1 
                    ELSE ST_Length(geometry::geography) 
                END AS reverse_cost
         FROM proyectoalgoritmos.infraestructura',
        %s, %s, directed := true
    ) AS dij
    JOIN proyectoalgoritmos.infraestructura AS infra ON dij.edge = infra.id;
""", (source_id, target_id))

# Obtener los resultados de la ruta
ruta = cur.fetchall()
print("Ruta encontrada con", len(ruta), "elementos.")

# Calcular la distancia total en metros sumando los costos
distancia_total_metros = sum(row[3] for row in ruta)  # Costos ya están en metros
distancia_total_km = distancia_total_metros / 1000  # Convertir a kilómetros
distancia_total_km= distancia_total_km*0.7765151515151515

print("Distancia total de la ruta en kilómetros:", distancia_total_km)


# Preparar los datos de la ruta para el cálculo de resiliencia
ruta_data = [(row[2], row[3]) for row in ruta]  # [(edge_id, cost)]

# Calcular resiliencia usando la función importada
resiliencia = calcular_resiliencia(ruta_data, fallas_infra, tipos_amenazas, multiplicadores_amenazas)

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

geojson_result = {
    "type": "FeatureCollection",
    "features": features
}

geojson_path = "./static/dijkstra.geojson"
with open(geojson_path, "w", encoding="utf-8") as geojson_file:
    json.dump(geojson_result, geojson_file, ensure_ascii=False, indent=4)
print(f"Resultado exportado como '{geojson_path}'")

#Eliminar txt si existe
if os.path.exists("./static/dijkstra_resiliencia.txt"):
    os.remove("./static/dijkstra_resiliencia.txt")

# Exportar las métricas de resiliencia a un archivo de texto
resiliencia_path = "./static/dijkstra_resiliencia.txt"
if os.path.exists(resiliencia_path):
    os.remove(resiliencia_path)

with open(resiliencia_path, "w", encoding="utf-8") as txt_file:
    txt_file.write("Métricas de resiliencia de la ruta frente a amenazas:\n")
    txt_file.write(f" - Resiliencia en costo (relativa): {resiliencia_costo:.2f}\n")
    txt_file.write(f" - Resiliencia en impacto (elementos no afectados): {resiliencia_impacto:.2f}\n")
    txt_file.write(f" - Distancia total de la ruta: {distancia_total_km:.2f} km\n")

print(f"Métricas de resiliencia exportadas como '{resiliencia_path}'")

# Cerrar el cursor y la conexión a la base de datos
cur.close()
conn.close()
