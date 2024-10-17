from pykml import parser
import geojson
import psycopg2
from shapely.geometry import LineString, shape, mapping
from dotenv import load_dotenv
import os
import json

load_dotenv('../.env')

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

def convertir_kml_a_geojson(kml_path, geojson_path):
    features = []
    try:
        with open(kml_path, 'rt', encoding='utf-8') as f:
            root = parser.parse(f).getroot()

        for placemark in root.Document.Placemark:
            if hasattr(placemark, 'LineString'):
                coords = placemark.LineString.coordinates.text.strip().split()
                line_coords = [(float(c.split(',')[0]), float(c.split(',')[1])) for c in coords]
                line = LineString(line_coords)

                name = str(placemark.name) if hasattr(placemark, 'name') else 'Sin nombre'

                feature = geojson.Feature(geometry=mapping(line), properties={"name": name})
                features.append(feature)

        feature_collection = geojson.FeatureCollection(features)

        with open(geojson_path, 'w', encoding='utf-8') as geojson_file:
            geojson.dump(feature_collection, geojson_file)

        return geojson_path

    except Exception as e:
        print(f"Error al convertir KML a GeoJSON: {e}")
        return None

def cargar_ciclovias_geojson_a_postgis(geojson_path):
    try:
        with open(geojson_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        for feature in geojson_data['features']:
            geom = shape(feature['geometry'])
            wkt_geom = geom.wkt

            cur.execute("""
                INSERT INTO proyectoalgoritmos.ciclovias (geometry)
                VALUES (ST_GeomFromText(%s, 4326))
            """, (wkt_geom,))
        conn.commit()

        os.remove(geojson_path)

    except Exception as e:
        print(f"Error al cargar ciclovías desde GeoJSON o al eliminar el archivo: {e}")

kml_path = '../Infraestructura/Archivos_descargados/ciclovias_santiago.kml'
geojson_path = 'ciclovias_santiago.geojson'

geojson_generado = convertir_kml_a_geojson(kml_path, geojson_path)

if geojson_generado:
    cargar_ciclovias_geojson_a_postgis(geojson_generado)

cur.execute("SELECT COUNT(*) FROM proyectoalgoritmos.ciclovias")
ciclovias_count = cur.fetchone()[0]
print(f"Total de ciclovías cargadas: {ciclovias_count}")

cur.close()
conn.close()
