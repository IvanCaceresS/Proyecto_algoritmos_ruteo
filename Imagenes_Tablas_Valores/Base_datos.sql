-- Crear la extensión PostGIS si no está habilitada
CREATE EXTENSION IF NOT EXISTS postgis;

-- Crear la tabla infraestructura con id como BIGINT
CREATE TABLE infraestructura (
    id BIGINT PRIMARY KEY,  -- Ahora el id no es SERIAL, sino BIGINT para almacenar el id del GeoJSON
    name VARCHAR(255),
    type VARCHAR(50),
    lanes INT,
    is_ciclovia BOOLEAN DEFAULT FALSE,  -- Indicar si es una ciclovía o no
    geometry GEOMETRY(LineString, 4326)
);

-- Crear la tabla para almacenar los nodos (intersecciones)
CREATE TABLE infraestructura_nodos (
    id SERIAL PRIMARY KEY,  -- Este campo puede seguir siendo SERIAL ya que los nodos se generan automáticamente
    geometry GEOMETRY(Point, 4326)  -- Geometría de intersección (nodo)
);

-- Crear el índice espacial para mejorar el rendimiento
CREATE INDEX infraestructura_geometry_idx ON infraestructura USING GIST (geometry);
CREATE INDEX infraestructura_nodos_geometry_idx ON infraestructura_nodos USING GIST (geometry);
