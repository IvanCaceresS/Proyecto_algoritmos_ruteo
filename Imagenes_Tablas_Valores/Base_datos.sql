-- Eliminar el esquema 'proyectoalgoritmos' si ya existe, eliminando todo lo que contiene
DROP SCHEMA IF EXISTS proyectoalgoritmos CASCADE;

-- Crear el esquema 'proyectoalgoritmos' nuevamente
CREATE SCHEMA proyectoalgoritmos;

-- Crear la extensión PostGIS si no está habilitada
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgrouting;

-- Crear la tabla infraestructura con id como BIGINT en el esquema 'proyectoalgoritmos'
CREATE TABLE proyectoalgoritmos.infraestructura (
    id BIGINT PRIMARY KEY,  -- id del GeoJSON o segmento de la infraestructura
    name VARCHAR(255),      -- nombre del segmento
    type VARCHAR(50),       -- tipo de infraestructura (ej. residencial, terciaria)
    lanes INT,              -- número de carriles
    is_ciclovia BOOLEAN DEFAULT FALSE,  -- Indicar si es una ciclovía o no
    source BIGINT,          -- Nodo inicial
    target BIGINT,          -- Nodo final
    cost DOUBLE PRECISION,  -- Costo del segmento (ej. longitud de la geometría en metros)
    geometry GEOMETRY(LineString, 4326)  -- Geometría de la infraestructura
);

-- Crear la tabla para almacenar los nodos (intersecciones) en el esquema 'proyectoalgoritmos'
CREATE TABLE proyectoalgoritmos.infraestructura_nodos (
    id SERIAL PRIMARY KEY,  -- ID autoincremental de los nodos
    geometry GEOMETRY(Point, 4326)  -- Geometría de los puntos de intersección (nodos)
);

-- Crear los índices espaciales para mejorar el rendimiento en el esquema 'proyectoalgoritmos'
CREATE INDEX infraestructura_geometry_idx ON proyectoalgoritmos.infraestructura USING GIST (geometry);
CREATE INDEX infraestructura_nodos_geometry_idx ON proyectoalgoritmos.infraestructura_nodos USING GIST (geometry);


