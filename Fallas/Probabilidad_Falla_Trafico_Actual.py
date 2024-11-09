import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

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

trafico = pd.read_sql("SELECT * FROM proyectoalgoritmos.trafico_actual", conn)
infraestructura = pd.read_sql("SELECT id, name FROM proyectoalgoritmos.infraestructura", conn)

trafico['name_normalized'] = trafico['name'].str.lower().str.strip()
infraestructura['name_normalized'] = infraestructura['name'].str.lower().str.strip()

infra_trafico = pd.merge(infraestructura, trafico, on='name_normalized', how='inner', suffixes=('_infra', '_trafico'))

def calcular_probabilidad_falla_por_trafico(infra_trafico):
    resultados = []

    for _, row in infra_trafico.iterrows():
        current_speed = row['current_speed']
        free_flow_speed = row['free_flow_speed']
        
        if pd.notna(current_speed) and pd.notna(free_flow_speed) and free_flow_speed > 0:
            ratio = current_speed / free_flow_speed
            if ratio < 0.3:
                probabilidad_falla = 0.9
            elif ratio < 0.5:
                probabilidad_falla = 0.7
            elif ratio < 0.7:
                probabilidad_falla = 0.5
            elif ratio < 0.9:
                probabilidad_falla = 0.3
            else:
                probabilidad_falla = 0.1
        else:
            probabilidad_falla = 0.1
        resultados.append({
            'id_infraestructura': row['id_infra'],
            'id_nodo': None,
            'amenaza': 'trafico',
            'probabilidad_falla': probabilidad_falla
        })

    return resultados

resultados = calcular_probabilidad_falla_por_trafico(infra_trafico)

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
print("Probabilidades de falla basadas en tráfico almacenadas en la tabla probabilidad_falla.")

cur.close()
conn.close()
