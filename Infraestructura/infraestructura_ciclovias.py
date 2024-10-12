import requests

kml_url = "https://www.google.com/maps/d/u/0/kml?mid=1dOO_kEQi6qMUjHHje0YBVLmsvKc&resourcekey&lid=zvBMMeqnQFNI.kYm4_4QBWl2Y&forcekml=1"

response = requests.get(kml_url)

if response.status_code == 200:
    with open("./Archivos_descargados/ciclovias_santiago.kml", "wb") as file:
        file.write(response.content)
    print("Archivo KML descargado correctamente.")
else:
    print(f"Error al descargar el archivo. Código de estado: {response.status_code}")
