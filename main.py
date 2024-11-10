import os
import subprocess
from pathlib import Path

ruta_metadata = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Metadata')
ruta_amenazas = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Amenazas')
ruta_importacion = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Importacion_Data')
ruta_infraestructura = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Infraestructura')
ruta_algoritmos = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Algoritmos')
ruta_exportacion = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Exportacion_Data')
ruta_fallas = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Fallas')
ruta_sitio_web = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Sitio Web')

carpetas_y_extensiones = {
    "./Fallas": [".csv", ".geojson"],
    "./Sitio Web/static": [".geojson", ".txt"],
    "./Sitio Web/static/Archivos_exportados": [".geojson", ".json"],
    "./Metadata/Archivos_descargados": [".geojson"],
    "./Infraestructura/Archivos_descargados": [".geojson"],
    "./Amenazas/Archivos_descargados": [".json"],
    "./Exportacion_Data/Archivos_exportados": [".json", ".geojson"]
}

for carpeta, extensiones in carpetas_y_extensiones.items():
    carpeta_path = Path(carpeta)
    if carpeta_path.exists() and carpeta_path.is_dir():
        for archivo in carpeta_path.iterdir():
            if archivo.suffix in extensiones:
                archivo.unlink()
                print(f"Eliminado: {archivo}")
    else:
        print(f"La carpeta {carpeta} no existe o no es un directorio.")

python_path = os.path.abspath(Path("virtual_env") / "Scripts" / "python")
print("Python path:", python_path)  # Esto debería mostrar la ruta absoluta completa

def ejecutar_script(script, ruta_carpeta):
    directorio_actual = os.getcwd()
    try:
        os.chdir(ruta_carpeta)
        subprocess.run([str(python_path), script], check=True)
        print(f"{script} ejecutado con éxito en {ruta_carpeta}.")
    
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {script} en {ruta_carpeta}: {e}")
    
    finally:
        os.chdir(directorio_actual)

scripts_infraestructura = ["infraestructura_ciclovias.py", "infraestructura_vias.py"]
scripts_metadata = ["estacionamientos.py", "iluminacion.py", "inundaciones.py", "velocidad_max.py"]
scripts_amenazas = ["precipitaciones.py", "cierre-calles.py", "seguridad.py", "trafico-actual.py"]
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

scripts_fallas = [
    "Probabilidad_Falla_Cierre_Calles.py",
    "Probabilidad_Falla_Precipitaciones.py",
    "Probabilidad_Falla_Seguridad.py",
    "Probabilidad_Falla_Trafico_Actual.py",
    "Falla.py",
    "Fallas_geolocalizadas.py"
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

# 7. Ejecución de scripts de 'Fallas'
print("Ejecutando scripts de fallas...")
for script in scripts_fallas:
    ejecutar_script(script, ruta_fallas)
    
# 8. Leaflet corriendo en el puerto 8080 ./Sitio Web/app.py
print("Ejecutando Leaflet en el puerto 8080...")
ejecutar_script("app.py", ruta_sitio_web)

print("Todos los scripts han sido ejecutados en el orden especificado.")