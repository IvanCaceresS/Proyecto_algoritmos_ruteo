import os
import subprocess
import sys
import json
from flask import Flask, send_from_directory, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Archivos_exportados/<path:filename>')
def archivos_exportados(filename):
    return send_from_directory('static/Archivos_exportados', filename)

python_path = os.path.abspath("virtual_env/Scripts/python")

@app.route('/dijkstra', methods=['POST'])
def calculate_route():
    print("Calculando ruta con Dijkstra...")
    data = request.json
    start = data.get('start_id')
    end = data.get('end_id')

    if not start or not end:
        return jsonify({"success": False, "error": "Puntos de inicio y fin son requeridos."}), 400

    try:
        # Ejecutar el script dijkstra.py con los puntos de inicio y fin
        result = subprocess.run(
            [sys.executable, '../Algoritmos/dijkstra.py', str(start), str(end)],
            capture_output=True,
            text=True,
            check=True
        )
        print("Salida estándar:", result.stdout)  # Imprimir salida estándar para depuración
        dijktra_path = "./static/dijkstra.geojson"
        # Cargar el archivo 'dijkstra.geojson' generado por el script
        with open(dijktra_path, "r", encoding="utf-8") as geojson_file:
            geojson_data = json.load(geojson_file)

        return jsonify({"success": True, "geojson": geojson_data})
    except subprocess.CalledProcessError as e:
        print("Error al ejecutar el script:", e)
        print("Salida estándar:", e.stdout)  # Imprimir salida estándar para depuración
        print("Error estándar:", e.stderr)  # Imprimir error estándar para depuración
        return jsonify({"success": False, "error": "Error al calcular la ruta."}), 500

@app.route('/cplex', methods=['POST'])
def calculate_cplex_route():
    print("Calculando ruta con CPLEX...")
    data = request.json
    start = data.get('start_id')
    end = data.get('end_id')

    if not start or not end:
        return jsonify({"success": False, "error": "Puntos de inicio y fin son requeridos."}), 400

    try:
        # Ejecutar el script cplex_route.py con los puntos de inicio y fin
        result = subprocess.run(
            [sys.executable, '../Algoritmos/cplex_route.py', str(start), str(end)],
            capture_output=True,
            text=True,
            check=True
        )
        print("Salida estándar:", result.stdout)  # Imprimir salida estándar para depuración

        # Cargar el archivo 'cplex_route.geojson' generado por el script
        cplex_geojson_path = "./static/cplex_route.geojson"  # Ruta al archivo generado
        with open(cplex_geojson_path, "r", encoding="utf-8") as geojson_file:
            geojson_data = json.load(geojson_file)

        return jsonify({"success": True, "geojson": geojson_data})
    except subprocess.CalledProcessError as e:
        print("Error al ejecutar el script:", e)
        print("Salida estándar:", e.stdout)  # Imprimir salida estándar para depuración
        print("Error estándar:", e.stderr)  # Imprimir error estándar para depuración
        return jsonify({"success": False, "error": "Error al calcular la ruta con CPLEX."}), 500
    
@app.route('/dijkstra_complete', methods=['POST'])
def calculate_dijkstra_complete_route():
    print("Calculando ruta Dijkstra Completa...")
    data = request.json
    start = data.get('start_id')
    end = data.get('end_id')

    if not start or not end:
        return jsonify({"success": False, "error": "Puntos de inicio y fin son requeridos."}), 400

    try:
        # Ejecutar el script dijkstra_complete.py con los puntos de inicio y fin
        result = subprocess.run(
            [sys.executable, '../Algoritmos/dijkstra_complete.py', str(start), str(end)],
            capture_output=True,
            text=True,
            check=True
        )
        print("Salida estándar:", result.stdout)  # Imprimir salida estándar para depuración

        # Cargar el archivo 'dijkstra_complete.geojson' generado por el script
        dijkstra_complete_geojson_path = "./static/dijkstra_complete.geojson"  # Ruta al archivo generado
        with open(dijkstra_complete_geojson_path, "r", encoding="utf-8") as geojson_file:
            geojson_data = json.load(geojson_file)

        return jsonify({"success": True, "geojson": geojson_data})
    except subprocess.CalledProcessError as e:
        print("Error al ejecutar el script:", e)
        print("Salida estándar:", e.stdout)  # Imprimir salida estándar para depuración
        print("Error estándar:", e.stderr)  # Imprimir error estándar para depuración
        return jsonify({"success": False, "error": "Error al calcular la ruta Dijkstra Completa."}), 500
    
@app.route('/aco_route', methods=['POST'])
def calculate_aco_route():
    print("Calculando ruta ACO...")
    data = request.json
    start = data.get('start_id')
    end = data.get('end_id')

    if not start or not end:
        print("Puntos de inicio y fin son requeridos.")
        return jsonify({"success": False, "error": "Puntos de inicio y fin son requeridos."}), 400

    try:
        # Ejecutar el script ACO con los puntos de inicio y fin
        result = subprocess.run(
            [sys.executable, '../Algoritmos/aco_route.py', str(start), str(end)],
            capture_output=True,
            text=True,
            check=True
        )
        print("Salida estándar del script:", result.stdout)  # Imprimir salida estándar para depuración

        # Cargar el archivo 'aco_route.geojson' generado por el script
        aco_geojson_path = "./static/aco_route.geojson"  # Ruta al archivo generado
        if not os.path.exists(aco_geojson_path):
            print("No se generó el archivo geojson; sin ruta válida.")
            return jsonify({"success": False, "error": "No se pudo encontrar una ruta válida con ACO."})

        with open(aco_geojson_path, "r", encoding="utf-8") as geojson_file:
            geojson_data = json.load(geojson_file)
            print("Archivo geojson cargado exitosamente.")

        return jsonify({"success": True, "geojson": geojson_data})
    except subprocess.CalledProcessError as e:
        print("Error al ejecutar el script:", e)
        print("Salida estándar:", e.stdout)  # Imprimir salida estándar para depuración
        print("Error estándar:", e.stderr)  # Imprimir error estándar para depuración
        return jsonify({"success": False, "error": "Error al calcular la ruta ACO."}), 500



if __name__ == '__main__':

    app.run(port=8080)
