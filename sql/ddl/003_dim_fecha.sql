CREATE TABLE IF NOT EXISTS dim_fecha (
    fecha_key INTEGER PRIMARY KEY,
    fecha DATE NOT NULL,
    anio SMALLINT NOT NULL,
    trimestre SMALLINT NOT NULL,
    mes SMALLINT NOT NULL,
    nombre_mes VARCHAR(20) NOT NULL,
    semana_anio SMALLINT NOT NULL,
    dia_mes SMALLINT NOT NULL,
    dia_semana SMALLINT NOT NULL,
    nombre_dia VARCHAR(20) NOT NULL,
    es_fin_mes BOOLEAN NOT NULL,
    es_dia_habil BOOLEAN NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_dim_fecha_fecha
    ON dim_fecha (fecha);

CREATE INDEX IF NOT EXISTS ix_dim_fecha_anio_mes
    ON dim_fecha (anio, mes);
