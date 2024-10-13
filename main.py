import os
import subprocess
import threading

# Ruta a las carpetas 'Metadata' y 'Amenazas'
ruta_metadata = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Metadata')
ruta_amenazas = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Amenazas')
ruta_importacion = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Importacion_Data')

# Función para ejecutar un script en una carpeta específica
def ejecutar_script(script, ruta_carpeta):
    # Guardar el directorio de trabajo actual
    directorio_actual = os.getcwd()
    
    try:
        # Cambiar al directorio específico (Metadata o Amenazas)
        os.chdir(ruta_carpeta)

        # Ejecutar el script
        subprocess.run(["python", script], check=True)
        print(f"{script} ejecutado con éxito en {ruta_carpeta}.")
    
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {script} en {ruta_carpeta}: {e}")
    
    finally:
        # Volver al directorio de trabajo original
        os.chdir(directorio_actual)

# Lista de scripts a ejecutar en 'Metadata'
scripts_metadata = ["estacionamientos.py", "iluminacion.py", "inundaciones.py", "velocidad_max.py"]

# Lista de scripts a ejecutar en 'Amenazas'
scripts_amenazas = ["precipitaciones.py"]  # Agrega otros scripts si tienes más en esta carpeta

# Crear una lista para almacenar los hilos
threads = []

# Inicializar e iniciar los hilos para los scripts de 'Metadata'
for script in scripts_metadata:
    thread = threading.Thread(target=ejecutar_script, args=(script, ruta_metadata))
    threads.append(thread)
    thread.start()

# Inicializar e iniciar los hilos para los scripts de 'Amenazas'
for script in scripts_amenazas:
    thread = threading.Thread(target=ejecutar_script, args=(script, ruta_amenazas))
    threads.append(thread)
    thread.start()

# Esperar a que todos los hilos terminen
for thread in threads:
    thread.join()

print("Todos los scripts de 'Metadata' y 'Amenazas' han sido ejecutados.")