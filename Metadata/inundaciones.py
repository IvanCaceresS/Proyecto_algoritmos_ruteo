import requests
import json

url = "https://arclim.mma.gob.cl/features/attributes/comunas/?attributes=NOM_COMUNA,NOM_PROVIN,NOM_REGION,ind_amen_inundaciones_t05_fut,ind_amen_inundaciones_t05_pres,ind_amen_inundaciones_t10_delta,ind_amen_inundaciones_t10_fut,ind_amen_inundaciones_t10_pres,ind_amen_inundaciones_t20_fut,ind_amen_inundaciones_t20_pres,ind_exp_inundaciones,ind_vuln_inundaciones,ind_riesgo_inundaciones_t05_fut,ind_riesgo_inundaciones_t05_fut_norm,ind_riesgo_inundaciones_t05_pres,ind_riesgo_inundaciones_t05_pres_norm,ind_riesgo_inundaciones_t10_delta,ind_riesgo_inundaciones_t10_fut,ind_riesgo_inundaciones_t10_fut_norm,ind_riesgo_inundaciones_t10_pres,ind_riesgo_inundaciones_t10_pres_norm,ind_riesgo_inundaciones_t20_fut,ind_riesgo_inundaciones_t20_fut_norm,ind_riesgo_inundaciones_t20_pres,ind_riesgo_inundaciones_t20_pres_norm,ind_amen_inundaciones_t05_delta,ind_riesgo_inundaciones_t05_delta,ind_amen_inundaciones_t20_delta,ind_riesgo_inundaciones_t20_delta,ind_amen_inundaciones_altitud_max,ind_amen_inundaciones_altitud_media,ind_amen_inundaciones_altitud_min,ind_amen_inundaciones_area,ind_amen_inundaciones_erodab1,ind_amen_inundaciones_erodab2,ind_amen_inundaciones_latitud,ind_amen_inundaciones_longitud,ind_amen_inundaciones_pendiente_max,ind_amen_inundaciones_pendiente_media,ind_amen_inundaciones_pendiente_min,ind_amen_inundaciones_precip_T10,ind_amen_inundaciones_precip_T20,ind_amen_inundaciones_precip_T5,ind_amen_inundaciones_t05_delta,ind_amen_inundaciones_t05_fut,ind_amen_inundaciones_t05_pres,ind_amen_inundaciones_t10_delta,ind_amen_inundaciones_t10_fut,ind_amen_inundaciones_t10_pres,ind_amen_inundaciones_t20_fut,ind_amen_inundaciones_t20_delta,ind_amen_inundaciones_t20_pres,ind_exp_inundaciones,ind_exp_inundaciones_area,ind_exp_inundaciones_cuar_bomb,ind_exp_inundaciones_cuar_carab,ind_exp_inundaciones_dens_edu,ind_exp_inundaciones_dens_serv,ind_exp_inundaciones_dens_pob,ind_exp_inundaciones_est_edu,ind_exp_inundaciones_hab,ind_exp_inundaciones_hosp,ind_exp_inundaciones_matricula_est_edu,ind_exp_inundaciones_norm,ind_exp_inundaciones_serv_salud,ind_exp_inundaciones_viviendas,ind_riesgo_inundaciones_t05_delta,ind_riesgo_inundaciones_t05_fut,ind_riesgo_inundaciones_t05_fut_norm,ind_riesgo_inundaciones_t05_pres,ind_riesgo_inundaciones_t05_pres_norm,ind_riesgo_inundaciones_t10,ind_riesgo_inundaciones_t10_delta,ind_riesgo_inundaciones_t10_fut,ind_riesgo_inundaciones_t10_pres,ind_riesgo_inundaciones_t10_fut_norm,ind_riesgo_inundaciones_t10_pres_norm,ind_riesgo_inundaciones_t20,ind_riesgo_inundaciones_t20_delta,ind_riesgo_inundaciones_t20_fut,ind_riesgo_inundaciones_t20_fut_norm,ind_riesgo_inundaciones_t20_pres,ind_riesgo_inundaciones_t20_pres_norm,ind_vuln_inundaciones,ind_vuln_inundaciones_norm,ind_vuln_inundaciones_P01_1,ind_vuln_inundaciones_P01_2,ind_vuln_inundaciones_P01_3,ind_vuln_inundaciones_P01_4,ind_vuln_inundaciones_P01_5,ind_vuln_inundaciones_P01_6,ind_vuln_inundaciones_P01_7,ind_vuln_inundaciones_P03A_1,ind_vuln_inundaciones_P03A_2,ind_vuln_inundaciones_P03A_3,ind_vuln_inundaciones_P03A_4,ind_vuln_inundaciones_P03A_5,ind_vuln_inundaciones_P03A_6,ind_vuln_inundaciones_sens_cuart_bomb,ind_vuln_inundaciones_sens_cuart_carab,ind_vuln_inundaciones_sens_est_edu,ind_vuln_inundaciones_sens_sc_hosp,ind_vuln_inundaciones_sens_sc_serv_salud,ind_vuln_inundaciones_total_viviendas,ind_vuln_hab,ComCod&format=geojson&file_name=ARCLIM_inundaciones_urbanas_comunas"

try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error al descargar el archivo: {e}")
    exit(1)

data = response.json()

filtered_features = []
desired_properties = [
    "NOM_REGION",
    "NOM_COMUNA",
    "NOM_PROVIN",
    "ind_riesgo_inundaciones_t10_delta"
]

for feature in data['features']:
    properties = feature['properties']
    if properties.get('NOM_REGION') == 'REGIÓN METROPOLITANA DE SANTIAGO':
        new_properties = {key: properties.get(key) for key in desired_properties}
        new_feature = {
            'type': 'Feature',
            'geometry': feature['geometry'],
            'properties': new_properties
        }
        filtered_features.append(new_feature)

filtered_data = {
    'type': 'FeatureCollection',
    'features': filtered_features
}

output_filename = './Archivos_descargados/inundaciones.geojson'
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(filtered_data, f, ensure_ascii=False, indent=4)
    print(f"Archivo GeoJSON filtrado guardado como '{output_filename}'.")
