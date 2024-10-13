import requests
import re
import json

cookies = {
    'laravel_session': 'eyJpdiI6IlJzbEZLazVWZUpUYjBGYWx2djFPWWFGOEhDc2xVcUdKd0dJTUxPd2F6Qzg9IiwidmFsdWUiOiI1MjVjZVpRTE43eTM2eTVYcm5nMGtXVUpRSkVhUWx6aXFjWldFU3J3NmZkbFJKbm5DYUhVZ3pmc01mUTZ1cVFmRzdBVEExd3N5NVY4Zm1HVlBad1htZz09IiwibWFjIjoiYTA5MmQ5M2EyN2MzZGZkZmM2Y2FmYjAzZGRhOTg1YjZiZmMzMGYxMTJjMTZkZTEwZDU5MjhkMDJmYWUzYWU5NSJ9',
}

headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'es-US,es-419;q=0.9,es;q=0.8,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'dnt': '1',
    'origin': 'https://datoscomunales.pazciudadana.cl/',
    'priority': 'u=1, i',
    'referer': 'https://datoscomunales.pazciudadana.cl/',
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

data = {
    'typeInfo': 'casospoliciales',
    'typeCrime': 'dmcs',
    'typeTime': '2023-10-01',
    'typeFreq': 'quarter',
    'typeReg': '1',
    'typeView': 'rmgraph',
}

response = requests.post('https://datoscomunales.pazciudadana.cl/datoscomunales/', cookies=cookies, headers=headers, data=data)

# Patrón para capturar tanto 'data-name' como 'data-value'
pattern = r'data-name="([^"]+)"[^>]+data-value="([^"]+)"'

# Encontrar todas las coincidencias
matches = re.findall(pattern, response.json()['view'])

# Crear un diccionario con los datos encontrados
data_dict = {data_name: data_value for data_name, data_value in matches}

# Guardar el diccionario en un archivo JSON
with open('Archivos_descargados/indices-comunas.json', 'w', encoding='utf-8') as json_file:
    json.dump(data_dict, json_file, ensure_ascii=False, indent=4)

print("Datos guardados en resultados.json")
