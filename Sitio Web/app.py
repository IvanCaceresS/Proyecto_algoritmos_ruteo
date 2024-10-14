import os
import shutil
from flask import Flask, send_from_directory, render_template

app = Flask(__name__)

# Ruta de los archivos originales
EXPORTACION_DATA_SRC = "../Exportacion_Data/Archivos_exportados"
ALGORITMOS_SRC = "../Algoritmos/dijkstra.geojson"

# Ruta de destino en la carpeta static
EXPORTACION_DATA_DEST = "./static/Archivos_exportados"
ALGORITMOS_DEST = "./static/dijkstra.geojson"

# Función para copiar archivos a la carpeta static
def preparar_archivos():
    # Eliminar el contenido de la carpeta ./static/Archivos_exportados si existe
    if os.path.exists(EXPORTACION_DATA_DEST):
        shutil.rmtree(EXPORTACION_DATA_DEST)  # Elimina la carpeta y su contenido

    # Crear de nuevo la carpeta y copiar el contenido
    shutil.copytree(EXPORTACION_DATA_SRC, EXPORTACION_DATA_DEST)
    print(f"Carpeta {EXPORTACION_DATA_DEST} copiada correctamente.")

    # Eliminar el archivo ./static/dijkstra.geojson si ya existe
    if os.path.exists(ALGORITMOS_DEST):
        os.remove(ALGORITMOS_DEST)  # Elimina el archivo existente

    # Copiar el archivo dijkstra.geojson
    shutil.copy(ALGORITMOS_SRC, ALGORITMOS_DEST)
    print(f"Archivo {ALGORITMOS_DEST} copiado correctamente.")

# Rutas en Flask
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Archivos_exportados/<path:filename>')
def archivos_exportados(filename):
    return send_from_directory('static/Archivos_exportados', filename)

@app.route('/dijkstra.geojson')
def dijkstra():
    return send_from_directory('static', 'dijkstra.geojson')

if __name__ == '__main__':
    # Ejecutar la función para preparar los archivos antes de iniciar el servidor
    preparar_archivos()

    # Iniciar el servidor Flask
    app.run(port=8080)
