CREATE TABLE IF NOT EXISTS dim_empresa (
    empresa_key BIGSERIAL PRIMARY KEY,
    ruc VARCHAR(11),
    razon_social VARCHAR(255) NOT NULL,
    company_code_bvl VARCHAR(50),
    nemonico VARCHAR(50),
    isin VARCHAR(50),
    sector_key BIGINT,
    sector_smv VARCHAR(150),
    sector_bvl VARCHAR(150),
    subsector_bvl VARCHAR(150),
    fecha_inscripcion_smv DATE,
    estado_registro VARCHAR(50),
    origen_empresa VARCHAR(50),
    es_emisora_bvl BOOLEAN NOT NULL DEFAULT FALSE,
    sitio_web VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_dim_empresa_sector
        FOREIGN KEY (sector_key) REFERENCES dim_sector (sector_key)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_dim_empresa_ruc
    ON dim_empresa (ruc)
    WHERE ruc IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_dim_empresa_company_code_bvl
    ON dim_empresa (company_code_bvl)
    WHERE company_code_bvl IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_dim_empresa_nemonico
    ON dim_empresa (nemonico)
    WHERE nemonico IS NOT NULL;

CREATE INDEX IF NOT EXISTS ix_dim_empresa_sector_key
    ON dim_empresa (sector_key);
