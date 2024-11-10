import os
import pandas as pd
import psycopg2
import random
from dotenv import load_dotenv
import warnings

# Suprimir warnings específicos de pandas
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

# Eliminar archivos anteriores si existen
try:
    os.remove('../Sitio Web/static/Fallas/probabilidad_falla_actualizada.csv')
    os.remove('../Sitio Web/static/Fallas/amenazas_ocurriendo.csv')
except FileNotFoundError:
    pass

# Cargar las variables de entorno
load_dotenv(dotenv_path='../.env')

# Configuración de conexión a la base de datos
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

# Asegurarse de que existe la columna `sucede_falla`
cur.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'proyectoalgoritmos'
              AND table_name = 'probabilidad_falla'
              AND column_name = 'sucede_falla'
        ) THEN
            ALTER TABLE proyectoalgoritmos.probabilidad_falla
            ADD COLUMN sucede_falla BOOLEAN;
        END IF;
    END $$;
""")
conn.commit()

# Leer la tabla de probabilidades de falla
query = "SELECT * FROM proyectoalgoritmos.probabilidad_falla"
probabilidad_falla_df = pd.read_sql(query, conn)

# Eliminar duplicados, quedando solo una fila por combinación de id_infraestructura, id_nodo, y amenaza
probabilidad_falla_df = probabilidad_falla_df.drop_duplicates(subset=['id_infraestructura', 'id_nodo', 'amenaza'])

# Función para determinar si ocurre la falla
def determinar_sucede_falla(probabilidad):
    numero_aleatorio = random.uniform(0, 100)
    return numero_aleatorio <= probabilidad * 100

# Aplicar la función para obtener la columna `sucede_falla`
probabilidad_falla_df['sucede_falla'] = probabilidad_falla_df['probabilidad_falla'].apply(determinar_sucede_falla)

# Actualizar la tabla en la base de datos con el nuevo valor de `sucede_falla`
update_query = """
    UPDATE proyectoalgoritmos.probabilidad_falla
    SET sucede_falla = %s
    WHERE id = %s
"""
for index, row in probabilidad_falla_df.iterrows():
    cur.execute(update_query, (row['sucede_falla'], row['id']))
conn.commit()

# Exportar el CSV actualizado con probabilidades de falla
probabilidad_falla_df.to_csv('../Sitio Web/static/Fallas/probabilidad_falla_actualizada.csv', index=False, encoding='utf-8')
print("Datos exportados a 'probabilidad_falla_actualizada.csv'.")

# Filtrar solo las amenazas que están ocurriendo y exportarlas
amenazas_ocurriendo_df = probabilidad_falla_df[probabilidad_falla_df['sucede_falla'] == True]
amenazas_ocurriendo_df.to_csv('../Sitio Web/static/Fallas/amenazas_ocurriendo.csv', index=False, encoding='utf-8')
print("Datos de amenazas que están ocurriendo exportados a 'amenazas_ocurriendo.csv'.")

# Cerrar la conexión a la base de datos
cur.close()
conn.close()
