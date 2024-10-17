import os
import shutil
from flask import Flask, send_from_directory, render_template

app = Flask(__name__)

EXPORTACION_DATA_SRC = "../Exportacion_Data/Archivos_exportados"
ALGORITMOS_SRC = "../Algoritmos/dijkstra.geojson"

EXPORTACION_DATA_DEST = "./static/Archivos_exportados"
ALGORITMOS_DEST = "./static/dijkstra.geojson"

def preparar_archivos():
    if os.path.exists(EXPORTACION_DATA_DEST):
        shutil.rmtree(EXPORTACION_DATA_DEST)

    shutil.copytree(EXPORTACION_DATA_SRC, EXPORTACION_DATA_DEST)
    print(f"Carpeta {EXPORTACION_DATA_DEST} copiada correctamente.")

    if os.path.exists(ALGORITMOS_DEST):
        os.remove(ALGORITMOS_DEST)

    shutil.copy(ALGORITMOS_SRC, ALGORITMOS_DEST)
    print(f"Archivo {ALGORITMOS_DEST} copiado correctamente.")

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
    preparar_archivos()

    app.run(port=8080)
