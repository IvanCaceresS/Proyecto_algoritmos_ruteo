import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import warnings

# Suprimir warnings específicos de pandas
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

# Cargar variables de entorno
load_dotenv(dotenv_path='../.env')

# Configurar conexión a la base de datos
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

# Consultas para obtener comunas asociadas a nodos y a infraestructura
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

# Obtener datos de seguridad y normalizar índice de delitos
seguridad = pd.read_sql("SELECT * FROM proyectoalgoritmos.seguridad_comunas_rm", conn)
min_indice = seguridad['indice_delitos'].min()
max_indice = seguridad['indice_delitos'].max()
seguridad['indice_delitos_normalizado'] = (seguridad['indice_delitos'] - min_indice) / (max_indice - min_indice)

# Relacionar seguridad con infraestructura y nodos
infra_seguridad = pd.merge(infra_comuna, seguridad, left_on="comuna", right_on="comuna", how="inner")
nodos_seguridad = pd.merge(nodos_comuna, seguridad, left_on="comuna", right_on="comuna", how="inner")

# Función para calcular probabilidad de falla de seguridad limitada al 70%
def calcular_probabilidad_falla_por_seguridad_normalizada(infra_seguridad, nodos_seguridad):
    resultados = []

    for _, row in infra_seguridad.iterrows():
        probabilidad_falla = row['indice_delitos_normalizado'] * 0.1  # Limitar al 70%
        resultados.append({
            'id_infraestructura': row['infraestructura_id'],
            'id_nodo': None,
            'amenaza': 'seguridad',
            'probabilidad_falla': probabilidad_falla
        })

    for _, row in nodos_seguridad.iterrows():
        probabilidad_falla = row['indice_delitos_normalizado'] * 0.1  # Limitar al 70%
        resultados.append({
            'id_infraestructura': None,
            'id_nodo': row['nodo_id'],
            'amenaza': 'seguridad',
            'probabilidad_falla': probabilidad_falla
        })
    
    return resultados

# Calcular y almacenar resultados en la base de datos
resultados = calcular_probabilidad_falla_por_seguridad_normalizada(infra_seguridad, nodos_seguridad)

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
print("Probabilidades de falla por índice de delitos normalizado almacenadas en la tabla probabilidad_falla.")

cur.close()
conn.close()
