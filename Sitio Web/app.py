import os
import shutil
import subprocess
import json
from flask import Flask, send_from_directory, render_template, request, jsonify

app = Flask(__name__)

EXPORTACION_DATA_SRC = "../Exportacion_Data/Archivos_exportados"

EXPORTACION_DATA_DEST = "./static/Archivos_exportados"
ALGORITMOS_DEST = "./static/dijkstra.geojson"

def preparar_archivos():
    if os.path.exists(EXPORTACION_DATA_DEST):
        shutil.rmtree(EXPORTACION_DATA_DEST)

    shutil.copytree(EXPORTACION_DATA_SRC, EXPORTACION_DATA_DEST)
    print(f"Carpeta {EXPORTACION_DATA_DEST} copiada correctamente.")

    if os.path.exists(ALGORITMOS_DEST):
        os.remove(ALGORITMOS_DEST)

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

@app.route('/calculate-route', methods=['POST'])
def calculate_route():
    data = request.json
    start = data.get('start_id')
    end = data.get('end_id')

    if not start or not end:
        return jsonify({"success": False, "error": "Puntos de inicio y fin son requeridos."}), 400

    try:
        # Ejecutar el script dijkstra.py con los puntos de inicio y fin
        result = subprocess.run(
            ['python', '../Algoritmos/dijkstra.py', str(start), str(end)],
            capture_output=True,
            text=True,
            check=True
        )
        print("Salida estándar:", result.stdout)  # Imprimir salida estándar para depuración
        # Cargar el archivo 'dijkstra.geojson' generado por el script
        with open(ALGORITMOS_DEST, "r", encoding="utf-8") as geojson_file:
            geojson_data = json.load(geojson_file)

        return jsonify({"success": True, "geojson": geojson_data})
    except subprocess.CalledProcessError as e:
        print("Error al ejecutar el script:", e)
        print("Salida estándar:", e.stdout)  # Imprimir salida estándar para depuración
        print("Error estándar:", e.stderr)  # Imprimir error estándar para depuración
        return jsonify({"success": False, "error": "Error al calcular la ruta."}), 500


if __name__ == '__main__':
    preparar_archivos()

    app.run(port=8080)
