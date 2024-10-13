import requests
import time
import csv
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='../.env')

api_key = os.getenv("WEATHER_API_KEY")

# Lista de comunas
comunas_rm = [
    "ALHUÉ",
    "BUIN",
    "CALERA DE TANGO",
    "CERRILLOS",
    "CERRO NAVIA",
    "COLINA",
    "CONCHALÍ",
    "CURACAVÍ",
    "EL BOSQUE",
    "EL MONTE",
    "ESTACIÓN CENTRAL",
    "HUECHURABA",
    "INDEPENDENCIA",
    "ISLA DE MAIPO",
    "LA CISTERNA",
    "LA FLORIDA",
    "LA GRANJA",
    "LA PINTANA",
    "LA REINA",
    "LAMPA",
    "LAS CONDES",
    "LO BARNECHEA",
    "LO ESPEJO",
    "LO PRADO",
    "MACUL",
    "MAIPÚ",
    "MARÍA PINTO",
    "MELIPILLA",
    "PADRE HURTADO",
    "PAINE",
    "PEDRO AGUIRRE CERDA",
    "PEÑAFLOR",
    "PEÑALOLÉN",
    "PIRQUE",
    "PROVIDENCIA",
    "PUDAHUEL",
    "PUENTE ALTO",
    "QUILICURA",
    "QUINTA NORMAL",
    "RECOLETA",
    "RENCA",
    "SAN BERNARDO",
    "SAN JOAQUÍN",
    "SAN JOSÉ DE MAIPO",
    "SAN MIGUEL",
    "SAN PEDRO",
    "SAN RAMÓN",
    "SANTIAGO",
    "TALAGANTE",
    "TILTIL",
    "VITACURA",
    "ÑUÑOA"
]

def obtener_coordenadas(comuna):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': f"{comuna}, Región Metropolitana, Chile",
        'format': 'json',
        'limit': 1,
    }
    headers = {
        'User-Agent': 'MiAplicacion/1.0 (tuemail@dominio.com)'
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    if data:
        lat = data[0]['lat']
        lon = data[0]['lon']
        return lat, lon
    else:
        return None, None

def obtener_precipitacion(lat, lon, api_key):
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        'key': api_key,
        'q': f"{lat},{lon}",
        'lang': 'es'
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'current' in data:
        precip_mm = data['current']['precip_mm']
        return precip_mm
    else:
        return None

# Lista para almacenar los resultados
resultados = []

#for comuna in comunas_rm:
for comuna in comunas_rm[:1]: #Limitar a 1 comuna para pruebas
    print(f"Procesando comuna: {comuna}")
    lat, lon = obtener_coordenadas(comuna)
    if lat and lon:
        precip_mm = obtener_precipitacion(lat, lon, api_key)
        if precip_mm is not None:
            resultados.append({
                'comuna': comuna,
                'latitud': lat,
                'longitud': lon,
                'precip_mm': precip_mm
            })
            print(f"Precipitación en {comuna}: {precip_mm} mm")
        else:
            print(f"No se pudo obtener la precipitación para {comuna}")
    else:
        print(f"No se pudieron obtener las coordenadas para {comuna}")
    time.sleep(1)  # Espera 1 segundo entre solicitudes a Nominatim

# Guardar los resultados en un archivo CSV
with open('./Archivos_descargados/precipitacion_comunas_rm.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['comuna', 'latitud', 'longitud', 'precip_mm']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for row in resultados:
        writer.writerow(row)

print("Datos de precipitación guardados en 'precipitacion_comunas_rm.csv'")
