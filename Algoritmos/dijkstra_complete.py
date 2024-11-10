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

# Cargar los datos de amenazas activas y geolocalizadas
fallas_df = pd.read_csv('./static/Fallas/amenazas_ocurriendo.csv')

# Cargar el archivo de iluminación y extraer IDs de calles iluminadas
with open('./static/Archivos_exportados/iluminacion.geojson', 'r') as f:
    iluminacion_data = json.load(f)

calles_iluminadas = [feature['properties']['geojson_id'] for feature in iluminacion_data['features'] if feature['properties']['lit'] == "yes"]

# Cargar el archivo de estacionamientos y extraer IDs de nodos cercanos a estacionamientos de bicicletas
with open('./static/Archivos_exportados/estacionamientos.geojson', 'r') as f:
    estacionamientos_data = json.load(f)

nodos_estacionamiento = [int(feature['properties']['geojson_id'].split('/')[-1]) for feature in estacionamientos_data['features'] if feature['properties']['amenity'] == "bicycle_parking"]

# Abrir el archivo de amenazas geolocalizadas con codificación UTF-8
with open('./static/Fallas/amenazas_geolocalizadas.geojson', 'r', encoding='utf-8') as f:
    amenazas_geo = json.load(f)


# Filtrar los IDs de infraestructuras afectadas por tipo de geometría
infraestructuras_amenazadas_lineas = [
    feature['properties']['id'] 
    for feature in amenazas_geo['features'] 
    if feature['properties']['sucede_falla'] and feature['geometry']['type'] == 'LineString'
]
nodos_amenazados_puntos = [
    feature['properties']['id']
    for feature in amenazas_geo['features']
    if feature['properties']['sucede_falla'] and feature['geometry']['type'] == 'Point'
]

# Construir diccionarios de tipos de amenaza y multiplicadores
tipos_amenazas = {feature['properties']['id']: feature['properties']['amenaza'] for feature in amenazas_geo['features']}
multiplicadores_amenazas = {
    'cierre_calle': 3,
    'seguridad': 2,
    'trafico': 1.5,
    'precipitacion_inundacion': 2.5
}

print(f"Calculando ruta desde el nodo {source_id} hasta el nodo {target_id}")

# Configurar condiciones para excluir las infraestructuras amenazadas y nodos afectados
infra_amenazada_cond = f"i.id NOT IN ({', '.join(map(str, infraestructuras_amenazadas_lineas))})" if infraestructuras_amenazadas_lineas else "TRUE"
nodos_amenazados_cond = f"i.source NOT IN ({', '.join(map(str, nodos_amenazados_puntos))}) AND i.target NOT IN ({', '.join(map(str, nodos_amenazados_puntos))})" if nodos_amenazados_puntos else "TRUE"

# Ajustar costos de acuerdo a cada tipo de amenaza, ciclovías, iluminación y cercanía a estacionamientos
adjusted_cost_conditions = []
fallas_infra_seguridad = [feature['properties']['id'] for feature in amenazas_geo['features'] if feature['properties']['amenaza'] == 'seguridad']
fallas_infra_trafico = [feature['properties']['id'] for feature in amenazas_geo['features'] if feature['properties']['amenaza'] == 'trafico']
fallas_infra_precipitacion = [feature['properties']['id'] for feature in amenazas_geo['features'] if feature['properties']['amenaza'] == 'precipitacion_inundacion']

if fallas_infra_seguridad:
    adjusted_cost_conditions.append(f"WHEN i.id IN ({', '.join(map(str, fallas_infra_seguridad))}) THEN i.cost * 1.5")
if fallas_infra_trafico:
    adjusted_cost_conditions.append(f"WHEN i.id IN ({', '.join(map(str, fallas_infra_trafico))}) THEN i.cost * 1.2")
if fallas_infra_precipitacion:
    adjusted_cost_conditions.append(f"WHEN i.id IN ({', '.join(map(str, fallas_infra_precipitacion))}) THEN i.cost * 1.1")

# Reducir el costo para ciclovías, iluminación y cercanía a estacionamientos
adjusted_cost_case = """
    CASE 
        WHEN i.is_ciclovia THEN i.cost * 0.5
        WHEN i.id IN ({iluminadas}) THEN i.cost * 0.7
        WHEN i.source IN ({nodos_est}) OR i.target IN ({nodos_est}) THEN i.cost * 0.8
        {amenaza_conditions}
        ELSE i.cost 
    END AS adjusted_cost
""".format(
    iluminadas=", ".join(map(str, calles_iluminadas)),
    nodos_est=", ".join(map(str, nodos_estacionamiento)),
    amenaza_conditions=" ".join(adjusted_cost_conditions)
)

# Crear una vista temporal con los costos ajustados y excluyendo infraestructuras y nodos amenazados
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
    WHERE {infra_amenazada_cond} AND {nodos_amenazados_cond};
""")

# Ejecutar pgr_dijkstra utilizando la vista con los costos ajustados
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

# Calcular la distancia total de la ruta en grados y convertir a kilómetros
distancia_total_grados = sum(row[3] for row in ruta)
distancia_total_km = distancia_total_grados * 111.32  # Conversión de grados a kilómetros
print("Distancia total de la ruta en kilómetros:", distancia_total_km)

# Preparar los datos de la ruta para el cálculo de resiliencia
ruta_data = [(row[2], row[3]) for row in ruta]  # [(edge_id, cost)]

# Calcular resiliencia usando la función importada
resiliencia = calcular_resiliencia(ruta_data, infraestructuras_amenazadas_lineas + nodos_amenazados_puntos, tipos_amenazas, multiplicadores_amenazas)

# Extraer métricas de resiliencia
resiliencia_costo = resiliencia["resiliencia_costo"]
resiliencia_impacto = resiliencia["resiliencia_impacto"]
elementos_afectados = resiliencia["elementos_afectados"]

# Crear la estructura de GeoJSON
features = []
for row in ruta:
    geometry = row[4]
    afectado = row[2] in (infraestructuras_amenazadas_lineas + nodos_amenazados_puntos)
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

geojson_path = "./static/dijkstra_complete.geojson"
if os.path.exists(geojson_path):
    os.remove(geojson_path)

with open(geojson_path, "w", encoding="utf-8") as geojson_file:
    json.dump(geojson_result, geojson_file, ensure_ascii=False, indent=4)
print(f"Resultado exportado como '{geojson_path}'")

#Eliminar txt si existe
if os.path.exists("./static/dijkstra_complete_resiliencia.txt"):
    os.remove("./static/dijkstra_complete_resiliencia.txt")
    print("Archivo eliminado")
else:
    print("No existe el archivo")

# Exportar las métricas de resiliencia a un archivo de texto
resiliencia_path = "./static/dijkstra_complete_resiliencia.txt"
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
