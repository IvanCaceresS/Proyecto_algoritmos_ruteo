import pandas as pd
import json
from pathlib import Path
import shutil
import os

EXPORTACION_DATA_SRC = "../Exportacion_Data/Archivos_exportados"
EXPORTACION_DATA_DEST = "../Sitio Web/static/Archivos_exportados"

def preparar_archivos():
    if os.path.exists(EXPORTACION_DATA_DEST):
        shutil.rmtree(EXPORTACION_DATA_DEST)

    shutil.copytree(EXPORTACION_DATA_SRC, EXPORTACION_DATA_DEST)
    print(f"Carpeta {EXPORTACION_DATA_DEST} copiada correctamente.")


preparar_archivos()

ruta_amenazas_csv = Path("../Sitio Web/static/Fallas/amenazas_ocurriendo.csv")
ruta_infraestructura_geojson = Path("../Sitio Web/static/Archivos_exportados/infraestructura.geojson")
ruta_nodos_geojson = Path("../Sitio Web/static/Archivos_exportados/infraestructura_nodos.geojson")
ruta_salida_geojson = Path("../Sitio Web/static/Fallas/amenazas_geolocalizadas.geojson")

amenazas_df = pd.read_csv(ruta_amenazas_csv)

with open(ruta_infraestructura_geojson, "r", encoding="utf-8") as f:
    infraestructura_geojson = json.load(f)

with open(ruta_nodos_geojson, "r", encoding="utf-8") as f:
    nodos_geojson = json.load(f)

amenazas_features = []

for amenaza in amenazas_df.itertuples():
    id_infra = amenaza.id_infraestructura
    id_nodo = amenaza.id_nodo

    if not pd.isna(id_infra):
        feature_infra = next((f for f in infraestructura_geojson["features"] if f["properties"]["id"] == int(id_infra)), None)
        if feature_infra:
            new_feature = feature_infra.copy()
            new_feature["properties"].update({
                "amenaza": amenaza.amenaza,
                "probabilidad_falla": amenaza.probabilidad_falla,
                "sucede_falla": amenaza.sucede_falla
            })
            amenazas_features.append(new_feature)

    if not pd.isna(id_nodo):
        feature_nodo = next((f for f in nodos_geojson["features"] if f["properties"]["id"] == int(id_nodo)), None)
        if feature_nodo:
            new_feature = feature_nodo.copy()
            new_feature["properties"].update({
                "amenaza": amenaza.amenaza,
                "probabilidad_falla": amenaza.probabilidad_falla,
                "sucede_falla": amenaza.sucede_falla
            })
            amenazas_features.append(new_feature)

amenazas_geojson = {
    "type": "FeatureCollection",
    "features": amenazas_features
}

with open(ruta_salida_geojson, "w", encoding="utf-8") as f:
    json.dump(amenazas_geojson, f, ensure_ascii=False, indent=4)

print(f"Amenazas exportadas como GeoJSON en '{ruta_salida_geojson}'")
