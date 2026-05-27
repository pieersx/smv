# SMV 360°

Proyecto de Inteligencia de Negocios orientado al mercado de valores peruano.

Este repositorio contiene el avance hasta `S8-S9`:

- Diseno del Data Warehouse
- Modelado dimensional
- Diccionario de datos preliminar
- Scripts DDL para PostgreSQL

## Estructura actual

```text
data/
  raw/
    smv/
    bvl/
    bcrp/
    inei/
    sbs/
  interim/
  processed/
    marts/

docs/
  fuentes.md
  modelo_dimensional.md
  diccionario_datos.md

sql/
  ddl/
    001_dim_sector.sql
    002_dim_empresa.sql
    003_dim_fecha.sql
    004_fact_indicadores_financieros.sql
    005_fact_precios_bvl.sql
    006_fact_macro.sql
  marts/
```

## Alcance de esta fase

En esta etapa no se implementa ETL ni carga de datos. Solo se deja preparado el diseno del DW y la base SQL para la siguiente fase.
