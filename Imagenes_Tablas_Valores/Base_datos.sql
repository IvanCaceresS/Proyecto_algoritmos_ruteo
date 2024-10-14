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

CREATE TABLE proyectoalgoritmos.ciclovias (
    id SERIAL PRIMARY KEY,
    geometry GEOMETRY(LineString, 4326)
);

-- Crear la tabla 'estacionamientos' para almacenar los datos de estacionamientos
CREATE TABLE proyectoalgoritmos.estacionamientos (
    id SERIAL PRIMARY KEY,                     -- Identificador único
    geojson_id VARCHAR(50),                    -- ID del GeoJSON
    name VARCHAR(255),                         -- Nombre del estacionamiento
    amenity VARCHAR(50),                       -- Tipo de servicio, ej. 'bicycle_parking'
    capacity INT,                              -- Capacidad del estacionamiento
    network VARCHAR(50),                       -- Nombre de la red, ej. 'Bicimetro'
    geometry GEOMETRY(Point, 4326)             -- Geometría en formato Point con SRID 4326
);

-- Crear la tabla 'iluminacion' para almacenar los datos de iluminación
CREATE TABLE proyectoalgoritmos.iluminacion (
    id SERIAL PRIMARY KEY,                   -- Identificador único
    geojson_id BIGINT,                       -- ID del GeoJSON
    lit VARCHAR(10),                         -- Si está iluminado o no (yes/no)
    geometry GEOMETRY(LineString, 4326)      -- Geometría en formato LineString con SRID 4326
);

CREATE TABLE proyectoalgoritmos.inundaciones (
    id SERIAL PRIMARY KEY,                       -- Identificador único
    nom_region VARCHAR(255),                     -- Nombre de la región
    nom_comuna VARCHAR(255),                     -- Nombre de la comuna
    nom_provin VARCHAR(255),                     -- Nombre de la provincia
    ind_riesgo_inundaciones_t10_delta NUMERIC,   -- Indicador de riesgo de inundación
    geometry GEOMETRY(Polygon, 4326)             -- Geometría en formato Polygon con SRID 4326
);

-- Crear la tabla 'velocidades_maximas' para almacenar los datos de velocidades máximas
CREATE TABLE proyectoalgoritmos.velocidades_maximas (
    id SERIAL PRIMARY KEY,                     -- Identificador único
    geojson_id BIGINT,                         -- ID del GeoJSON
    maxspeed VARCHAR(10),                      -- Velocidad máxima
    geometry GEOMETRY(LineString, 4326)        -- Geometría en formato LineString con SRID 4326
);

-- Crear la tabla 'cierres_calles' para almacenar los datos de cierres de calles
CREATE TABLE proyectoalgoritmos.cierres_calles (
    id BIGINT PRIMARY KEY,               -- ID del registro
    name VARCHAR(255),                   -- Nombre de la calle
    coordenada GEOMETRY(Point, 4326),    -- Coordenadas (latitud, longitud) en formato Point con SRID 4326
    road_closure VARCHAR(3)              -- Indicador de cierre de calle (Yes/No)
);

-- Crear la tabla 'precipitacion_comunas_rm' para almacenar los datos de precipitación de las comunas
CREATE TABLE proyectoalgoritmos.precipitacion_comunas_rm (
    id SERIAL PRIMARY KEY,                    -- Identificador único
    comuna VARCHAR(255),                      -- Nombre de la comuna
    latitud DOUBLE PRECISION,                 -- Latitud de la comuna
    longitud DOUBLE PRECISION,                -- Longitud de la comuna
    precip_mm DOUBLE PRECISION                -- Precipitación en milímetros
);

-- Crear la tabla 'seguridad_comunas_rm' para almacenar el índice de delitos de las comunas
CREATE TABLE proyectoalgoritmos.seguridad_comunas_rm (
    id SERIAL PRIMARY KEY,                   -- Identificador único
    comuna VARCHAR(255),                     -- Nombre de la comuna
    indice_delitos DOUBLE PRECISION          -- Índice de delitos
);

-- Crear la tabla 'trafico_actual' para almacenar los datos de tráfico actual
CREATE TABLE proyectoalgoritmos.trafico_actual (
    id BIGINT PRIMARY KEY,               -- Identificador único del segmento
    name VARCHAR(255),                   -- Nombre de la calle
    coordenada GEOMETRY(Point, 4326),    -- Coordenadas (latitud, longitud) en formato Point con SRID 4326
    current_speed INT,                   -- Velocidad actual en el segmento
    free_flow_speed INT                  -- Velocidad en condiciones de tráfico libre
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