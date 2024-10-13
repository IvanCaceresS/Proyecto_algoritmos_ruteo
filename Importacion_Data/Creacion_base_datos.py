import psycopg2
from dotenv import load_dotenv
import os

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

sql_file_path = '../Imagenes_Tablas_Valores/Base_datos.sql'

with open(sql_file_path, 'r') as sql_file:
    sql_commands = sql_file.read()

cur.execute(sql_commands)

conn.commit()

cur.close()
conn.close()

print("El archivo SQL ha sido ejecutado correctamente.")
