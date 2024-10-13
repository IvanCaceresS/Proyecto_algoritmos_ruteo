import os
import subprocess
import threading

# Ruta a las carpetas 'Metadata', 'Amenazas', 'Importacion_Data' e 'Infraestructura'
ruta_metadata = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Metadata')
ruta_amenazas = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Amenazas')
ruta_importacion = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Importacion_Data')
ruta_infraestructura = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Infraestructura')
ruta_bbdd = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Imagenes_Tablas_Valores')

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
scripts_infraestructura = ["infraestructura_ciclovias.py", "infraestructura_calles.py"]

# Lista de scripts a ejecutar en 'Metadata'
scripts_metadata = ["estacionamientos.py", "iluminacion.py", "inundaciones.py", "velocidad_max.py"]

# Lista de scripts a ejecutar en 'Amenazas'
scripts_amenazas = ["precipitaciones.py"]  # Agrega otros scripts si tienes más en esta carpeta

# Lista de scripts a ejecutar en 'Importacion_Data'
scripts_importacion = ["importacion_infraestructura.py"]

# Crear una lista para almacenar los hilos
threads = []

# Ejecutar scripts en orden secuencial: Creación de BBDD, Infraestructura, Metadata, Amenazas, Importaciones

# 1. Ejecución de la creación de la base de datos (sin hilos, para asegurar que se ejecute primero)
print("Ejecutando scripts de creación de base de datos...")
for script in ["Creacion_base_datos.py"]:
    ejecutar_script(script, ruta_bbdd)

# 2. Ejecución de scripts de 'Infraestructura'
print("Ejecutando scripts de infraestructura...")
for script in scripts_infraestructura:
    thread = threading.Thread(target=ejecutar_script, args=(script, ruta_infraestructura))
    threads.append(thread)
    thread.start()

# Esperar a que los hilos de 'Infraestructura' terminen
for thread in threads:
    thread.join()

# Limpiar la lista de hilos para la siguiente fase
threads.clear()

# 3. Ejecución de scripts de 'Metadata'
print("Ejecutando scripts de metadata...")
for script in scripts_metadata:
    thread = threading.Thread(target=ejecutar_script, args=(script, ruta_metadata))
    threads.append(thread)
    thread.start()

# Esperar a que los hilos de 'Metadata' terminen
for thread in threads:
    thread.join()

# Limpiar la lista de hilos para la siguiente fase
threads.clear()

# 4. Ejecución de scripts de 'Amenazas'
print("Ejecutando scripts de amenazas...")
for script in scripts_amenazas:
    thread = threading.Thread(target=ejecutar_script, args=(script, ruta_amenazas))
    threads.append(thread)
    thread.start()

# Esperar a que los hilos de 'Amenazas' terminen
for thread in threads:
    thread.join()

# Limpiar la lista de hilos para la siguiente fase
threads.clear()

# 5. Ejecución de scripts de 'Importacion_Data' (esto se ejecuta al final)
print("Ejecutando scripts de importación de infraestructura...")
for script in scripts_importacion:
    thread = threading.Thread(target=ejecutar_script, args=(script, ruta_importacion))
    threads.append(thread)
    thread.start()

# Esperar a que los hilos de 'Importacion_Data' terminen
for thread in threads:
    thread.join()

print("Todos los scripts han sido ejecutados en el orden especificado.")
