import requests
import json

# URL de descarga de 13.geojson
url = "https://raw.githubusercontent.com/caracena/chile-geojson/refs/heads/master/13.geojson"

# Lista de comunas a conservar
# comunas_deseadas = [
#     "Alhué", "Buin", "Calera de Tango", "Cerrillos", "Cerro Navia", "Colina", 
#     "Conchalí", "Curacaví", "El Bosque", "El Monte", "Estación Central", 
#     "Huechuraba", "Independencia", "Isla de Maipo", "La Cisterna", "La Florida", 
#     "La Granja", "La Pintana", "La Reina", "Lampa", "Las Condes", "Lo Barnechea", 
#     "Lo Espejo", "Lo Prado", "Macul", "Maipú", "María Pinto", "Melipilla", 
#     "Padre Hurtado", "Paine", "Pedro Aguirre Cerda", "Peñaflor", "Peñalolén", 
#     "Pirque", "Providencia", "Pudahuel", "Puente Alto", "Quilicura", 
#     "Quinta Normal", "Recoleta", "Renca", "San Bernardo", "San Joaquín", 
#     "San José de Maipo", "San Miguel", "San Pedro", "San Ramón", "Santiago", 
#     "Talagante", "Tiltil", "Vitacura", "Ñuñoa"
# ]

comunas_deseadas = ["Santiago"]

# Descargar el archivo geojson
try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    print(f"Error al descargar el archivo: {e}")
    exit(1)

# Filtrar las comunas deseadas
filtered_features = [
    feature for feature in data['features']
    if feature.get('properties', {}).get('Comuna') in comunas_deseadas
]

# Sobrescribir 13.geojson con las comunas deseadas
filtered_data = {
    'type': 'FeatureCollection',
    'features': filtered_features
}

output_filename = './Archivos_descargados/13.geojson'
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(filtered_data, f, ensure_ascii=False, indent=4)
    print(f"Archivo GeoJSON filtrado guardado y sobrescrito como '{output_filename}'.")
