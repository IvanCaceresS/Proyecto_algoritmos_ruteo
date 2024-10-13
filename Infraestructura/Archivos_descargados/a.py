import json

# Cargar el archivo GeoJSON
with open('calles_primarias_secundarias_santiago.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

# Verificar si es un FeatureCollection
if geojson_data['type'] == 'FeatureCollection':
    # Contar cuántos features hay en la colección
    num_features = len(geojson_data['features'])
    print(f"El número de features (posibles calles) es: {num_features}")
else:
    print("El archivo no es un FeatureCollection válido.")
