-- Eliminar todas las tablas en el esquema 'public', excepto las que son requeridas por PostGIS
DO $$ DECLARE
    r RECORD;
BEGIN
    -- Eliminar todas las tablas en el esquema 'public' excepto las relacionadas a PostGIS
    FOR r IN (SELECT tablename 
              FROM pg_tables 
              WHERE schemaname = 'public' 
              AND tablename NOT IN ('spatial_ref_sys', 'geography_columns', 'geometry_columns', 'raster_columns', 'raster_overviews')) LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END $$;

-- Crear la extensión PostGIS si no está habilitada
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgrouting;

-- Crear la tabla infraestructura con id como BIGINT
CREATE TABLE infraestructura (
    id BIGINT PRIMARY KEY,  -- id del GeoJSON o segmento de la infraestructura
    name VARCHAR(255),
    type VARCHAR(50),
    lanes INT,
    is_ciclovia BOOLEAN DEFAULT FALSE,  -- Indicar si es una ciclovía o no
    source BIGINT,  -- Nodo inicial
    target BIGINT,  -- Nodo final
    geometry GEOMETRY(LineString, 4326)  -- Geometría de la infraestructura
);

-- Crear la tabla para almacenar los nodos (intersecciones)
CREATE TABLE infraestructura_nodos (
    id SERIAL PRIMARY KEY,  -- ID autoincremental de los nodos
    geometry GEOMETRY(Point, 4326)  -- Geometría de los puntos de intersección (nodos)
);

-- Crear los índices espaciales para mejorar el rendimiento
CREATE INDEX infraestructura_geometry_idx ON infraestructura USING GIST (geometry);
CREATE INDEX infraestructura_nodos_geometry_idx ON infraestructura_nodos USING GIST (geometry);

-- Crear una tabla de coste para pgRouting (usada en pgr_dijkstra)
CREATE TABLE infrastructure_cost AS
    SELECT id, source, target, ST_Length(geometry) AS cost
    FROM infraestructura;
