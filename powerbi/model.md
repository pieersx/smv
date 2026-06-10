# Modelo Power BI recomendado

## Tablas

Hechos:

- `fact_financial_kpis`
- `fact_sector_risk`
- `fact_macro_bcrp`
- `fact_sbs_financial_system`
- `fact_inei_pbi_department`
- `fact_mef_state_enterprises`
- `fact_bvl_market_snapshot`

Dimensiones:

- `dim_empresa`
- `source_coverage`
- `data_profile_tables`
- `data_quality_results`

## Relaciones sugeridas

1. `dim_empresa[rpj]` -> `fact_financial_kpis[rpj]`
   Cardinalidad: uno a muchos.

2. `fact_financial_kpis[periodo_label]` como filtro de periodo para paginas financieras.

3. `fact_sector_risk[ejercicio]` y `fact_sector_risk[periodo]` se usan como filtros independientes por sector.

4. `fact_macro_bcrp[anio]` se puede relacionar logicamente con `fact_financial_kpis[ejercicio]`, pero para evitar ambiguedad se recomienda usarlo como tabla independiente en visuales macro.

## Tipos recomendados

- Fechas:
  - `fact_macro_bcrp[fecha]`
  - `fact_sbs_financial_system[fecha]`

- Numericos decimales:
  - ratios financieros
  - montos
  - score de riesgo

- Texto:
  - empresas
  - sectores
  - fuentes
  - estados de calidad
