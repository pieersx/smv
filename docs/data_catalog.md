# Catalogo de datos - SMV 360

## Bronze

| Archivo | Fuente | Descripcion |
|---|---|---|
| `data/bronze/smv/principales_cuentas/*.json` | SMV Open Data | Principales cuentas financieras por empresa, ejercicio y periodo. |
| `data/bronze/bcrp/series/*.json` | BCRP API | Series macroeconomicas crudas en JSON. |
| `data/bronze/bvl/boletin_diario/bolres.htm` | BVL | Boletin diario oficial con resumen de mercado. |
| `data/bronze/sbs/*.zip` | SBS Datos Abiertos | Estados financieros del sistema financiero en ZIP. |
| `data/bronze/inei/pbi/pbi_peru_16.xlsx` | INEI | PBI Peru por departamentos/actividades en Excel. |
| `data/bronze/mef/balance_empresas_estado_sample.json` | MEF / Datos Abiertos | Balance constructivo de empresas del Estado via API. |

## Silver

| Archivo | Grano | Descripcion |
|---|---|---|
| `data/silver/smv_principales_cuentas.csv` | Empresa x periodo | Limpieza de nombres, RUC, sectores, montos financieros y periodos normalizados. |
| `data/silver/bcrp_series_long.csv` | Fecha x serie | Series BCRP en formato largo. |
| `data/silver/bcrp_series_wide.csv` | Fecha | Series BCRP pivoteadas por columna. |
| `data/silver/bvl_boletin_diario_tables.csv` | Tabla x fila | Tablas parseadas desde el boletin diario BVL. |
| `data/silver/sbs_*_inventory.csv` | Archivo dentro de ZIP | Inventario de archivos oficiales descargados desde SBS. |
| `data/silver/inei_pbi_peru_raw_rows.csv` | Hoja x fila | Filas auditables extraidas del workbook INEI. |
| `data/silver/mef_balance_empresas_estado_sample.csv` | Registro API | Muestra descargada desde la API de Datos Abiertos MEF. |

## Gold

| Archivo | Uso |
|---|---|
| `data/gold/dim_empresa.csv` | Dimension empresa para modelo estrella. |
| `data/gold/fact_financial_kpis.csv` | KPIs financieros por empresa y periodo. |
| `data/gold/fact_sector_risk.csv` | Agregados de riesgo por sector y periodo. |
| `data/gold/fact_macro_bcrp.csv` | Contexto macroeconomico BCRP para dashboard. |
| `data/gold/dashboard_summary.csv` | Resumen ejecutivo del periodo mas reciente. |
| `data/gold/source_coverage.csv` | Auditoria de las 6 fuentes del proyecto. |

## Cobertura de fuentes

| Fuente | Dataset materializado | Uso actual |
|---|---|---|
| SMV | Principales cuentas financieras 2019-2024 | Base del score de riesgo y KPIs financieros. |
| BCRP | Tipo de cambio, tasa, cobre, oro, IPC | Contexto macro del dashboard. |
| BVL | Boletin diario oficial | Evidencia de fuente bursatil; pendiente integracion historica profunda. |
| SBS | Estados financieros del sistema financiero | Fuente complementaria para riesgo financiero sectorial. |
| INEI | PBI Peru por departamentos/actividades | Fuente complementaria macro/territorial. |
| MEF / Datos Abiertos | Balance constructivo de empresas del Estado | Fuente complementaria de datos abiertos estatales. |

## KPIs calculados

| KPI | Formula |
|---|---|
| ROA | `utilidad_neta / activo_total` |
| ROE | `utilidad_neta / patrimonio_total` |
| Endeudamiento | `pasivo_total / activo_total` |
| Apalancamiento | `pasivo_total / patrimonio_total` |
| Margen neto | `utilidad_neta / total_ingreso` |
| Crecimiento ingresos | Variacion interanual por empresa y periodo |
| Crecimiento utilidad | Variacion interanual por empresa y periodo |

## Score de riesgo

El score actual es un indicador academico pragmatico de 0 a 100:

- Endeudamiento alto: hasta 35 puntos.
- ROA bajo o negativo: hasta 25 puntos.
- Margen neto bajo o negativo: hasta 20 puntos.
- Caida de utilidad: hasta 20 puntos.

Clasificacion:

- `Bajo`: menor a 40.
- `Medio`: 40 a 69.99.
- `Alto`: 70 o mas.

Este score es defendible como primera version BI. Para una version financiera mas estricta, el siguiente paso es integrar cuentas detalladas SMV y valor de mercado BVL para calcular Altman Z-Score completo.
