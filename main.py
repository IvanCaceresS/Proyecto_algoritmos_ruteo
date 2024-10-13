import os
import subprocess

# Ruta a las carpetas 'Metadata', 'Amenazas', 'Importacion_Data' e 'Infraestructura'
ruta_metadata = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Metadata')
ruta_amenazas = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Amenazas')
ruta_importacion = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Importacion_Data')
ruta_infraestructura = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Infraestructura')
ruta_algoritmos = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Algoritmos')

# Función para ejecutar un script en una carpeta específica
def ejecutar_script(script, ruta_carpeta):
    # Guardar el directorio de trabajo actual
    directorio_actual = os.getcwd()
    
    try:
        # Cambiar al directorio específico
        os.chdir(ruta_carpeta)

        # Ejecutar el script
        subprocess.run(["python", script], check=True)
        print(f"{script} ejecutado con éxito en {ruta_carpeta}.")
    
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {script} en {ruta_carpeta}: {e}")
    
    finally:
        # Volver al directorio de trabajo original
        os.chdir(directorio_actual)

# Lista de scripts a ejecutar en 'Infraestructura'
scripts_infraestructura = ["infraestructura_ciclovias.py", "infraestructura_vias.py"]

# Lista de scripts a ejecutar en 'Metadata'
scripts_metadata = ["estacionamientos.py", "iluminacion.py", "inundaciones.py", "velocidad_max.py"]

# Lista de scripts a ejecutar en 'Amenazas'
scripts_amenazas = ["precipitaciones.py", "cierre-calles.py", "seguridad.py", "trafico-actual.py"]

# Lista de scripts a ejecutar en 'Importacion_Data'
scripts_importacion = ["importacion_infraestructura.py"]

# Lista de scripts a ejecutar en 'Algoritmos'
scripts_algoritmos = ["dijkstra.py"]

# 1. Ejecución de la creación de la base de datos (Creacion_base_datos.py)
print("Ejecutando scripts de creación de base de datos...")
ejecutar_script("Creacion_base_datos.py", ruta_importacion)

# 2. Ejecución de scripts de 'Infraestructura'
print("Ejecutando scripts de infraestructura...")
for script in scripts_infraestructura:
    ejecutar_script(script, ruta_infraestructura)

# 3. Ejecución de scripts de 'Metadata'
print("Ejecutando scripts de metadata...")
for script in scripts_metadata:
    ejecutar_script(script, ruta_metadata)

# 4. Ejecución de scripts de 'Amenazas'
print("Ejecutando scripts de amenazas...")
for script in scripts_amenazas:
    ejecutar_script(script, ruta_amenazas)

# 5. Ejecución de scripts de 'Importacion_Data'
print("Ejecutando scripts de importación de infraestructura...")
for script in scripts_importacion:
    ejecutar_script(script, ruta_importacion)

# 6. Ejecución de scripts de 'Algoritmos'
print("Ejecutando scripts de algoritmos...")
for script in scripts_importacion:
    ejecutar_script(script, ruta_algoritmos)

print("Todos los scripts han sido ejecutados en el orden especificado.")

