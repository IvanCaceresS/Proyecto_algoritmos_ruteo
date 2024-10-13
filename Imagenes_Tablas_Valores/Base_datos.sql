-- Crear la extensión PostGIS (si no está habilitada)
CREATE EXTENSION IF NOT EXISTS postgis;

-- Crear la tabla infraestructura
CREATE TABLE infraestructura (
    id SERIAL PRIMARY KEY,  -- Identificador único
    name VARCHAR(255),  -- Nombre de la calle o ciclovía
    type VARCHAR(50),   -- Tipo de infraestructura (ej: 'calle', 'ciclovía')
    lanes INT,          -- Número de carriles (solo para calles, nulo para ciclovías)
    geometry GEOMETRY(LineString, 4326)  -- Geometría LineString (proyección WGS84)
);

-- Índice espacial para mejorar el rendimiento de consultas espaciales
CREATE INDEX infraestructura_geometry_idx ON infraestructura USING GIST (geometry);
