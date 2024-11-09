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

cierres_calles = pd.read_sql("SELECT * FROM proyectoalgoritmos.cierres_calles", conn)
infraestructura = pd.read_sql("SELECT id, name FROM proyectoalgoritmos.infraestructura", conn)

cierres_calles['name_normalized'] = cierres_calles['name'].str.lower().str.strip()
infraestructura['name_normalized'] = infraestructura['name'].str.lower().str.strip()

coincidencias = pd.merge(infraestructura, cierres_calles, on='name_normalized', how='inner', suffixes=('_infra', '_cierre'))

resultados = []
for _, row in coincidencias.iterrows():
    if row['road_closure'].strip().lower() == 'yes':
        probabilidad_falla = 0.9
    else:
        probabilidad_falla = 0.1
    
    resultados.append({
        'id_infraestructura': row['id_infra'],
        'id_nodo': None,
        'amenaza': 'cierre_calle',
        'probabilidad_falla': probabilidad_falla
    })

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
print("Probabilidades de falla por cierre de calles almacenadas en la tabla probabilidad_falla.")

cur.close()
conn.close()
