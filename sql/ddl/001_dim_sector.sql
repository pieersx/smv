CREATE TABLE IF NOT EXISTS dim_sector (
    sector_key BIGSERIAL PRIMARY KEY,
    sector_codigo VARCHAR(50),
    sector_nombre VARCHAR(150) NOT NULL,
    subsector_nombre VARCHAR(150),
    clasificacion_fuente VARCHAR(50),
    descripcion VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_dim_sector_nombre_fuente
    ON dim_sector (sector_nombre, COALESCE(clasificacion_fuente, 'NA'));
