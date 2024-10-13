import psycopg2

# Conectar a la base de datos PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="7541"
)
cur = conn.cursor()

# Ruta al archivo .sql
sql_file_path = '../Imagenes_Tablas_Valores/Base_datos.sql'

# Leer el archivo .sql
with open(sql_file_path, 'r') as sql_file:
    sql_commands = sql_file.read()

# Ejecutar el contenido del archivo .sql
cur.execute(sql_commands)

# Confirmar los cambios
conn.commit()

# Cerrar la conexión
cur.close()
conn.close()

print("El archivo SQL ha sido ejecutado correctamente.")
