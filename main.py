import os
import subprocess

# Ruta a las carpetas 'Metadata', 'Amenazas', 'Importacion_Data' e 'Infraestructura'
ruta_metadata = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Metadata')
ruta_amenazas = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Amenazas')
ruta_importacion = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Importacion_Data')
ruta_infraestructura = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Infraestructura')
ruta_algoritmos = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Algoritmos')
ruta_exportacion = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Exportacion_Data')
ruta_sitio_web = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Sitio Web')

def ejecutar_script(script, ruta_carpeta):
    directorio_actual = os.getcwd()
    try:
        os.chdir(ruta_carpeta)
        subprocess.run(["python", script], check=True)
        print(f"{script} ejecutado con éxito en {ruta_carpeta}.")
    
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {script} en {ruta_carpeta}: {e}")
    
    finally:
        os.chdir(directorio_actual)

# Lista de scripts a ejecutar en 'Infraestructura'
scripts_infraestructura = ["infraestructura_ciclovias.py", "infraestructura_vias.py"]

# Lista de scripts a ejecutar en 'Metadata'
scripts_metadata = ["estacionamientos.py", "iluminacion.py", "inundaciones.py", "velocidad_max.py"]

# Lista de scripts a ejecutar en 'Amenazas'
scripts_amenazas = ["precipitaciones.py", "cierre-calles.py", "seguridad.py", "trafico-actual.py"]

# Lista de scripts a ejecutar en 'Importacion_Data'
scripts_importacion = [
    "importacion_ciclovias.py",
    "importacion_infraestructura.py",
    "importacion_metadata_estacionamientos.py",
    "importacion_metadata_iluminacion.py",
    "importacion_metadata_inundacion.py",
    "importacion_metadata_velocidades.py",
    "importacion_amenaza_cierre_calles.py",
    "importacion_amenaza_precipitaciones.py",
    "importacion_amenaza_seguridad.py",
    "importacion_amenaza_trafico_actual.py"
    ]

# Lista de scripts a ejecutar en 'Algoritmos'
scripts_algoritmos = ["dijkstra.py"]

# Lista de scripts a ejecutar en 'Exportacion_Data'
scripts_exportacion = [
    "exportacion_infraestructura.py",
    "exportacion_ciclovias.py",
    "exportacion_metadata_estacionamientos.py",
    "exportacion_metadata_iluminacion.py",
    "exportacion_metadata_inundacion.py",
    "exportacion_metadata_velocidades.py",
    "exportacion_amenaza_cierre_calles.py",
    "exportacion_amenaza_precipitaciones.py",
    "exportacion_amenaza_seguridad.py",
    "exportacion_amenaza_trafico_actual.py"
    ]

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
print("Ejecutando scripts de importación...")
for script in scripts_importacion:
    ejecutar_script(script, ruta_importacion)

# 6. Ejecución de scripts de 'Exportacion_Data'
print("Ejecutando scripts de exportación...")
for script in scripts_exportacion:
    ejecutar_script(script, ruta_exportacion)
    
# 7. Ejecución de scripts de 'Algoritmos'
print("Ejecutando scripts de algoritmos...")
for script in scripts_algoritmos:
    ejecutar_script(script, ruta_algoritmos)    

# 8. Leaflet corriendo en el puerto 8080 ./Sitio Web/app.py
print("Ejecutando Leaflet en el puerto 8080...")
ejecutar_script("app.py", ruta_sitio_web)

print("Todos los scripts han sido ejecutados en el orden especificado.")

