# Power BI - SMV 360

Esta carpeta contiene los insumos para construir el dashboard en Power BI Desktop usando las tablas gold generadas por el pipeline.

## Paso 1: ejecutar pipeline

Desde la raiz del proyecto:

```powershell
python -m src.smv_bi.run_pipeline
```

Esto actualiza:

```text
data/gold/
```

## Paso 2: cargar datos en Power BI Desktop

Puedes abrir Power BI y la carpeta `data/gold/` con:

```powershell
.\powerbi\open_powerbi_workspace.ps1
```

En Power BI Desktop:

1. Obtener datos.
2. Texto/CSV.
3. Cargar las tablas desde `data/gold/`.

Tablas recomendadas:

- `fact_financial_kpis.csv`
- `dim_empresa.csv`
- `fact_sector_risk.csv`
- `fact_macro_bcrp.csv`
- `fact_sbs_financial_system.csv`
- `fact_inei_pbi_department.csv`
- `fact_mef_state_enterprises.csv`
- `fact_bvl_market_snapshot.csv`
- `source_coverage.csv`
- `data_profile_tables.csv`
- `data_quality_results.csv`

## Paso 3: crear medidas

Copiar las medidas de:

```text
powerbi/measures.dax
```

## Paso 4: crear paginas

Usar la guia:

```text
powerbi/dashboard_spec.md
```

## Nota

El archivo `.pbix` no se genera por script porque Power BI Desktop no ofrece un CLI oficial estable para construir reportes visuales completos desde cero. Este paquete deja el modelo, consultas y medidas listos para construirlo manualmente en Desktop.
