import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import warnings

# Suprimir warnings específicos de pandas
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

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

nodos_comuna_query = """
    SELECT 
        n.id AS nodo_id,
        i.nom_comuna AS comuna
    FROM 
        proyectoalgoritmos.infraestructura_nodos AS n
    JOIN 
        proyectoalgoritmos.inundaciones AS i
    ON 
        ST_Intersects(n.geometry, i.geometry);
"""
nodos_comuna = pd.read_sql(nodos_comuna_query, conn)

infra_comuna_query = """
    SELECT 
        infra.id AS infraestructura_id,
        i.nom_comuna AS comuna
    FROM 
        proyectoalgoritmos.infraestructura AS infra
    JOIN 
        proyectoalgoritmos.inundaciones AS i
    ON 
        ST_Intersects(infra.geometry, i.geometry);
"""
infra_comuna = pd.read_sql(infra_comuna_query, conn)
precipitacion = pd.read_sql("SELECT * FROM proyectoalgoritmos.precipitacion_comunas_rm", conn)
inundaciones = pd.read_sql("SELECT * FROM proyectoalgoritmos.inundaciones", conn)

riesgo_comunas = pd.merge(precipitacion, inundaciones, left_on="comuna", right_on="nom_comuna", how="inner")

def calcular_probabilidad_falla_por_precipitacion_inundacion(riesgo_comunas, infra_comuna, nodos_comuna):
    resultados = []

    for _, row in infra_comuna.iterrows():
        comuna_riesgo = riesgo_comunas[riesgo_comunas['comuna'] == row['comuna']]

        if not comuna_riesgo.empty:
            precip_mm = comuna_riesgo.iloc[0]['precip_mm']
            ind_riesgo_inundacion = comuna_riesgo.iloc[0]['ind_riesgo_inundaciones_t10_delta']

            if precip_mm == 0:
                probabilidad_falla = 0  # Probabilidad de falla es 0 si precipitación es 0
            else:
                if precip_mm > 50:
                    probabilidad_precipitacion = 0.8
                elif precip_mm >= 20:
                    probabilidad_precipitacion = 0.5
                else:
                    probabilidad_precipitacion = 0.2

                if ind_riesgo_inundacion > 5:
                    probabilidad_inundacion = 0.8
                elif ind_riesgo_inundacion >= 2:
                    probabilidad_inundacion = 0.5
                else:
                    probabilidad_inundacion = 0.2

                probabilidad_falla = (probabilidad_precipitacion + probabilidad_inundacion) / 2

            resultados.append({
                'id_infraestructura': row['infraestructura_id'],
                'id_nodo': None,
                'amenaza': 'precipitacion_inundacion',
                'probabilidad_falla': probabilidad_falla
            })

    for _, row in nodos_comuna.iterrows():
        comuna_riesgo = riesgo_comunas[riesgo_comunas['comuna'] == row['comuna']]

        if not comuna_riesgo.empty:
            precip_mm = comuna_riesgo.iloc[0]['precip_mm']
            ind_riesgo_inundacion = comuna_riesgo.iloc[0]['ind_riesgo_inundaciones_t10_delta']

            if precip_mm == 0:
                probabilidad_falla = 0  # Probabilidad de falla es 0 si precipitación es 0
            else:
                if precip_mm > 50:
                    probabilidad_precipitacion = 0.8
                elif precip_mm >= 20:
                    probabilidad_precipitacion = 0.5
                else:
                    probabilidad_precipitacion = 0.2

                if ind_riesgo_inundacion > 5:
                    probabilidad_inundacion = 0.8
                elif ind_riesgo_inundacion >= 2:
                    probabilidad_inundacion = 0.5
                else:
                    probabilidad_inundacion = 0.2

                probabilidad_falla = (probabilidad_precipitacion + probabilidad_inundacion) / 2

            resultados.append({
                'id_infraestructura': None,
                'id_nodo': row['nodo_id'],
                'amenaza': 'precipitacion_inundacion',
                'probabilidad_falla': probabilidad_falla
            })
    
    return resultados

resultados = calcular_probabilidad_falla_por_precipitacion_inundacion(riesgo_comunas, infra_comuna, nodos_comuna)

insert_query = """
    INSERT INTO proyectoalgoritmos.probabilidad_falla (id_infraestructura, id_nodo, amenaza, probabilidad_falla)
    VALUES (%s, %s, %s, %s)
"""

for result in resultados:
    cur.execute(insert_query, (
        result['id_infraestructura'],
        result['id_nodo'],
        result['amenaza'],
        result['probabilidad_falla']
    ))

conn.commit()
print("Probabilidades de falla por precipitación e inundación almacenadas en la tabla probabilidad_falla.")

cur.close()
conn.close()
