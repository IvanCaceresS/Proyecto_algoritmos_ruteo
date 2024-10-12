import requests
import json

# Definir las coordenadas del bounding box
norte = -33.2467   # Latitud máxima
sur = -33.8454     # Latitud mínima
este = -70.4333    # Longitud máxima
oeste = -70.9360   # Longitud mínima

# Crear la variable del bounding box en el orden: sur, oeste, norte, este
bbox = f"{sur},{oeste},{norte},{este}"

# Definir la consulta de Overpass
overpass_query = f"""
[out:json][timeout:25];
(
  way["highway"="primary"]({bbox});
  way["highway"="secondary"]({bbox});
);
out body;
>;
out skel qt;
"""

# Enviar la solicitud a Overpass API
overpass_url = "https://overpass-api.de/api/interpreter"
response = requests.get(overpass_url, params={'data': overpass_query})

# Verificar la respuesta y procesar el JSON
if response.status_code == 200:
    data = response.json()
    elements = data['elements']
    resultado = []

    # Procesar las vías
    for elem in elements:
        if elem['type'] == 'way':
            way_id = elem['id']
            tags = elem.get('tags', {})
            maxspeed = tags.get('maxspeed')
            # Solo incluir si 'maxspeed' está disponible
            if maxspeed:
                resultado.append({
                    'id': way_id,
                    'maxspeed': maxspeed
                })

    # Guardar el resultado en un archivo JSON
    with open('./Archivos_descargados/velocidades_maximas.json', 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=4)
    print("Archivo JSON guardado exitosamente.")
else:
    print(f"Error al obtener datos: {response.status_code}")
    print(response.text)
