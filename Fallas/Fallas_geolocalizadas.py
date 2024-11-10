import pandas as pd
import json
from pathlib import Path

# Rutas de los archivos
ruta_amenazas_csv = Path("../Sitio Web/static/Fallas/amenazas_ocurriendo.csv")
ruta_infraestructura_geojson = Path("../Sitio Web/static/Archivos_exportados/infraestructura.geojson")
ruta_nodos_geojson = Path("../Sitio Web/static/Archivos_exportados/infraestructura_nodos.geojson")
ruta_salida_geojson = Path("../Sitio Web/static/Fallas/amenazas_geolocalizadas.geojson")

# Cargar CSV de amenazas
amenazas_df = pd.read_csv(ruta_amenazas_csv)

# Cargar GeoJSON de infraestructura
with open(ruta_infraestructura_geojson, "r", encoding="utf-8") as f:
    infraestructura_geojson = json.load(f)

# Cargar GeoJSON de infraestructura_nodos
with open(ruta_nodos_geojson, "r", encoding="utf-8") as f:
    nodos_geojson = json.load(f)

# Lista para almacenar los features de amenazas
amenazas_features = []

# Realizar join para infraestructura
for amenaza in amenazas_df.itertuples():
    id_infra = amenaza.id_infraestructura
    id_nodo = amenaza.id_nodo

    # Buscar coincidencia en infraestructura
    if not pd.isna(id_infra):
        feature_infra = next((f for f in infraestructura_geojson["features"] if f["properties"]["id"] == int(id_infra)), None)
        if feature_infra:
            # Clonar el feature y agregar propiedades de amenaza
            new_feature = feature_infra.copy()
            new_feature["properties"].update({
                "amenaza": amenaza.amenaza,
                "probabilidad_falla": amenaza.probabilidad_falla,
                "sucede_falla": amenaza.sucede_falla
            })
            amenazas_features.append(new_feature)

    # Buscar coincidencia en nodos
    if not pd.isna(id_nodo):
        feature_nodo = next((f for f in nodos_geojson["features"] if f["properties"]["id"] == int(id_nodo)), None)
        if feature_nodo:
            # Clonar el feature y agregar propiedades de amenaza
            new_feature = feature_nodo.copy()
            new_feature["properties"].update({
                "amenaza": amenaza.amenaza,
                "probabilidad_falla": amenaza.probabilidad_falla,
                "sucede_falla": amenaza.sucede_falla
            })
            amenazas_features.append(new_feature)

# Crear el GeoJSON de salida
amenazas_geojson = {
    "type": "FeatureCollection",
    "features": amenazas_features
}

# Guardar el resultado en un archivo GeoJSON
with open(ruta_salida_geojson, "w", encoding="utf-8") as f:
    json.dump(amenazas_geojson, f, ensure_ascii=False, indent=4)

print(f"Amenazas exportadas como GeoJSON en '{ruta_salida_geojson}'")
