CREATE TABLE IF NOT EXISTS fact_precios_bvl (
    fact_precio_key BIGSERIAL PRIMARY KEY,
    empresa_key BIGINT NOT NULL,
    fecha_key INTEGER NOT NULL,
    precio_apertura NUMERIC(18,4),
    precio_cierre NUMERIC(18,4),
    precio_maximo NUMERIC(18,4),
    precio_minimo NUMERIC(18,4),
    precio_promedio NUMERIC(18,4),
    precio_anterior NUMERIC(18,4),
    variacion_pct NUMERIC(10,4),
    cantidad_negociada NUMERIC(18,4),
    monto_negociado_pen NUMERIC(18,2),
    monto_negociado_usd NUMERIC(18,2),
    numero_operaciones INTEGER,
    moneda VARCHAR(10),
    retorno_diario NUMERIC(10,6),
    volatilidad_30d NUMERIC(10,6),
    beta_30d NUMERIC(10,6),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_fact_precio_empresa
        FOREIGN KEY (empresa_key) REFERENCES dim_empresa (empresa_key),
    CONSTRAINT fk_fact_precio_fecha
        FOREIGN KEY (fecha_key) REFERENCES dim_fecha (fecha_key)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_fact_precios_grano
    ON fact_precios_bvl (empresa_key, fecha_key);

CREATE INDEX IF NOT EXISTS ix_fact_precios_empresa_key
    ON fact_precios_bvl (empresa_key);

CREATE INDEX IF NOT EXISTS ix_fact_precios_fecha_key
    ON fact_precios_bvl (fecha_key);
