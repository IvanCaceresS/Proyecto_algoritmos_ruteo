DROP SCHEMA IF EXISTS proyectoalgoritmos CASCADE;

CREATE SCHEMA proyectoalgoritmos;

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgrouting;

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

CREATE TABLE proyectoalgoritmos.infraestructura_nodos (
    id SERIAL PRIMARY KEY, 
    geometry GEOMETRY(Point, 4326)
);

-- CREATE TABLE proyectoalgoritmos.comuna (
-- 	id SERIAL PRIMARY KEY,
-- 	name VARCHAR(255),
--     geometry GEOMETRY(polygon, 4326) 
-- );

-- CREATE TABLE proyectoalgoritmos.infraestructura_metadata (
-- 	id_infraestructura BIGINT PRIMARY KEY,
--     maxSpeed INT,
-- 	currentSpeed INT,
--     lit BOOLEAN DEFAULT FALSE,
--     roadClosure BOOLEAN DEFAULT FALSE,
-- 	FOREIGN KEY (id_infraestructura) 
-- 	REFERENCES proyectoalgoritmos.infraestructura(id)
-- );

-- CREATE TABLE proyectoalgoritmos.comuna_metadata (
-- 	id_comuna SERIAL PRIMARY KEY,
-- 	precipitacion NUMERIC(3, 9),
-- 	delincuencia NUMERIC(3, 9),
-- 	FOREIGN KEY (id_infraestructura)
-- 	REFERENCES proyectoalgoritmos.comuna(id)
-- );

CREATE INDEX infraestructura_geometry_idx ON proyectoalgoritmos.infraestructura USING GIST (geometry);
CREATE INDEX infraestructura_nodos_geometry_idx ON proyectoalgoritmos.infraestructura_nodos USING GIST (geometry);