CREATE TABLE IF NOT EXISTS fact_indicadores_financieros (
    fact_financiero_key BIGSERIAL PRIMARY KEY,
    empresa_key BIGINT NOT NULL,
    fecha_key INTEGER NOT NULL,
    tipo_estado VARCHAR(20) NOT NULL,
    frecuencia_reporte VARCHAR(20) NOT NULL,
    moneda VARCHAR(10),
    fuente VARCHAR(20) NOT NULL DEFAULT 'SMV',
    activo_total NUMERIC(18,2),
    activo_corriente NUMERIC(18,2),
    pasivo_total NUMERIC(18,2),
    pasivo_corriente NUMERIC(18,2),
    patrimonio_neto NUMERIC(18,2),
    ventas_netas NUMERIC(18,2),
    utilidad_operativa NUMERIC(18,2),
    utilidad_neta NUMERIC(18,2),
    ebitda NUMERIC(18,2),
    deuda_financiera_total NUMERIC(18,2),
    capital_trabajo NUMERIC(18,2),
    utilidades_retenidas NUMERIC(18,2),
    roe NUMERIC(10,4),
    roa NUMERIC(10,4),
    current_ratio NUMERIC(10,4),
    deuda_ebitda NUMERIC(10,4),
    altman_z_score NUMERIC(10,4),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_fact_fin_empresa
        FOREIGN KEY (empresa_key) REFERENCES dim_empresa (empresa_key),
    CONSTRAINT fk_fact_fin_fecha
        FOREIGN KEY (fecha_key) REFERENCES dim_fecha (fecha_key),
    CONSTRAINT ck_fact_fin_tipo_estado
        CHECK (tipo_estado IN ('individual', 'consolidado')),
    CONSTRAINT ck_fact_fin_frecuencia
        CHECK (frecuencia_reporte IN ('trimestral', 'anual'))
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_fact_fin_grano
    ON fact_indicadores_financieros (empresa_key, fecha_key, tipo_estado, frecuencia_reporte);

CREATE INDEX IF NOT EXISTS ix_fact_fin_empresa_key
    ON fact_indicadores_financieros (empresa_key);

CREATE INDEX IF NOT EXISTS ix_fact_fin_fecha_key
    ON fact_indicadores_financieros (fecha_key);
