CREATE TABLE IF NOT EXISTS fact_macro (
    fact_macro_key BIGSERIAL PRIMARY KEY,
    fecha_key INTEGER NOT NULL,
    indicador_codigo VARCHAR(50) NOT NULL,
    indicador_nombre VARCHAR(150) NOT NULL,
    fuente VARCHAR(20) NOT NULL,
    frecuencia VARCHAR(20) NOT NULL,
    unidad_medida VARCHAR(50),
    valor NUMERIC(18,6) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_fact_macro_fecha
        FOREIGN KEY (fecha_key) REFERENCES dim_fecha (fecha_key),
    CONSTRAINT ck_fact_macro_frecuencia
        CHECK (frecuencia IN ('diaria', 'mensual', 'trimestral', 'anual'))
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_fact_macro_grano
    ON fact_macro (fecha_key, indicador_codigo, fuente);

CREATE INDEX IF NOT EXISTS ix_fact_macro_fecha_key
    ON fact_macro (fecha_key);

CREATE INDEX IF NOT EXISTS ix_fact_macro_indicador
    ON fact_macro (indicador_codigo);
