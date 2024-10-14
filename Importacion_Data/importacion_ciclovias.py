from pykml import parser
import geojson
import psycopg2
from shapely.geometry import LineString, shape, mapping
from dotenv import load_dotenv
import os
import json

# Cargar credenciales desde archivo .env
load_dotenv('../.env')

# Conexión a la base de datos
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

# Función para convertir KML a GeoJSON manualmente
def convertir_kml_a_geojson(kml_path, geojson_path):
    features = []
    try:
        # Leer el archivo KML usando pykml
        with open(kml_path, 'rt', encoding='utf-8') as f:
            root = parser.parse(f).getroot()

        # Recorrer los elementos del KML y extraer las líneas
        for placemark in root.Document.Placemark:
            # Comprobar si tiene geometría de tipo LineString
            if hasattr(placemark, 'LineString'):
                coords = placemark.LineString.coordinates.text.strip().split()
                # Convertir las coordenadas a formato adecuado para GeoJSON
                line_coords = [(float(c.split(',')[0]), float(c.split(',')[1])) for c in coords]
                line = LineString(line_coords)

                # Convertir el nombre del placemark a texto
                name = str(placemark.name) if hasattr(placemark, 'name') else 'Sin nombre'

                # Crear la feature GeoJSON para esta línea
                feature = geojson.Feature(geometry=mapping(line), properties={"name": name})
                features.append(feature)

        # Crear el FeatureCollection de GeoJSON
        feature_collection = geojson.FeatureCollection(features)

        # Guardar el GeoJSON en un archivo
        with open(geojson_path, 'w', encoding='utf-8') as geojson_file:
            geojson.dump(feature_collection, geojson_file)

        #print(f"Archivo KML convertido a GeoJSON: {geojson_path}")
        return geojson_path

    except Exception as e:
        print(f"Error al convertir KML a GeoJSON: {e}")
        return None

# Función para cargar ciclovías desde el archivo GeoJSON a PostGIS
def cargar_ciclovias_geojson_a_postgis(geojson_path):
    try:
        with open(geojson_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        # Iterar sobre las características del GeoJSON
        for feature in geojson_data['features']:
            geom = shape(feature['geometry'])  # Convertir a objeto Shapely
            wkt_geom = geom.wkt  # Convertir la geometría a WKT para PostGIS
            #print(f"Insertando ciclovía: {wkt_geom}")

            # Insertar la geometría en la tabla de PostGIS
            cur.execute("""
                INSERT INTO proyectoalgoritmos.ciclovias (geometry)
                VALUES (ST_GeomFromText(%s, 4326))
            """, (wkt_geom,))
        conn.commit()
        #print(f"{len(geojson_data['features'])} ciclovías cargadas en PostGIS.")

        # Eliminar el archivo GeoJSON después de insertar los datos
        os.remove(geojson_path)
        #print(f"Archivo {geojson_path} eliminado correctamente.")

    except Exception as e:
        print(f"Error al cargar ciclovías desde GeoJSON o al eliminar el archivo: {e}")

# Ruta al archivo KML y GeoJSON
kml_path = '../Infraestructura/Archivos_descargados/ciclovias_santiago.kml'
geojson_path = 'ciclovias_santiago.geojson'

# Convertir el archivo KML a GeoJSON
geojson_generado = convertir_kml_a_geojson(kml_path, geojson_path)

# Si la conversión fue exitosa, cargar los datos en PostGIS y eliminar el archivo GeoJSON
if geojson_generado:
    cargar_ciclovias_geojson_a_postgis(geojson_generado)

# Verificar si las ciclovías se han cargado correctamente
cur.execute("SELECT COUNT(*) FROM proyectoalgoritmos.ciclovias")
ciclovias_count = cur.fetchone()[0]
print(f"Total de ciclovías cargadas: {ciclovias_count}")

# Cerrar la conexión
cur.close()
conn.close()
