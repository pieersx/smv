# SMV 360 - Explicacion completa del proyecto BI

## 1. Resumen ejecutivo

SMV 360 es un proyecto de Inteligencia de Negocios orientado al analisis del mercado de valores peruano y del riesgo financiero corporativo. El objetivo es integrar datos abiertos oficiales de seis fuentes publicas para construir un pipeline reproducible con capas bronze, silver y gold, aplicar perfilado y reglas de calidad de datos, y presentar indicadores en dashboards.

El foco principal del dashboard es el riesgo financiero de empresas reportantes ante la Superintendencia del Mercado de Valores (SMV), complementado con contexto macroeconomico del BCRP y fuentes externas de BVL, SBS, INEI y MEF.

## 2. Problema de negocio

La informacion financiera del mercado peruano esta dispersa entre varios portales publicos. Un analista debe consultar manualmente datos de empresas, indicadores macroeconomicos, informacion bursatil, sistema financiero y estadisticas economicas.

El proyecto resuelve esta fragmentacion mediante un flujo BI que:

- Descarga datos abiertos oficiales.
- Normaliza estructuras heterogeneas.
- Calcula KPIs financieros.
- Genera tablas analiticas listas para dashboards.
- Audita calidad, cobertura, nulos y consistencia.

## 3. Fuentes oficiales usadas

| Fuente | Dataset usado | Uso en el proyecto |
|---|---|---|
| SMV | Principales cuentas financieras 2019-2024 | Base del score de riesgo corporativo. |
| BCRP | Tipo de cambio, tasa de referencia, cobre, oro, IPC | Contexto macroeconomico. |
| BVL | Boletin diario oficial | Snapshot bursatil y cobertura de mercado. |
| SBS | Estado de situacion financiera y estado de resultados del sistema financiero | Analisis complementario del sistema financiero. |
| INEI | PBI Peru por departamentos/actividades | Contexto macro-territorial. |
| MEF / Datos Abiertos | Balance constructivo de empresas del Estado | Datos abiertos estatales complementarios. |

La auditoria de fuentes queda materializada en:

```text
data/gold/source_coverage.csv
```

## 4. Arquitectura BI

El proyecto usa una arquitectura por capas:

```text
Fuentes oficiales
       |
       v
data/bronze   -> datos crudos descargados
       |
       v
data/silver   -> datos limpios y normalizados
       |
       v
data/gold     -> tablas analiticas, KPIs, profiling y calidad
       |
       v
Dashboard Streamlit / paquete Power BI
```

## 5. Capa bronze

La capa bronze conserva los datos crudos descargados desde las fuentes oficiales. Su objetivo es trazabilidad y reproducibilidad.

Ubicacion:

```text
data/bronze/
```

Ejemplos:

- `data/bronze/smv/principales_cuentas/*.json`
- `data/bronze/bcrp/series/*.json`
- `data/bronze/bvl/boletin_diario/bolres.htm`
- `data/bronze/sbs/*.zip`
- `data/bronze/inei/pbi/pbi_peru_16.xlsx`
- `data/bronze/mef/balance_empresas_estado_sample.json`

## 6. Capa silver

La capa silver transforma los datos crudos a formatos tabulares normalizados.

Ubicacion:

```text
data/silver/
```

Tablas principales:

| Archivo | Descripcion |
|---|---|
| `smv_principales_cuentas.csv` | Empresas SMV por periodo con activos, pasivos, patrimonio, ingresos y utilidad. |
| `bcrp_series_long.csv` | Series BCRP en formato largo. |
| `bcrp_series_wide.csv` | Series BCRP pivoteadas por fecha. |
| `sbs_financial_system_kpis.csv` | KPIs por entidad del sistema financiero SBS. |
| `inei_pbi_departamental.csv` | PBI departamental por anio. |
| `mef_empresas_estado_resumen.csv` | Resumen de empresas del Estado por departamento y entidad. |
| `bvl_market_snapshot.csv` | Indicadores extraidos del boletin diario BVL. |

## 7. Capa gold

La capa gold contiene las tablas listas para dashboard y analisis.

Ubicacion:

```text
data/gold/
```

Tablas principales:

| Tabla gold | Uso |
|---|---|
| `fact_financial_kpis.csv` | KPIs financieros por empresa SMV y periodo. |
| `dim_empresa.csv` | Dimension empresa. |
| `fact_sector_risk.csv` | Agregados de riesgo por sector. |
| `fact_macro_bcrp.csv` | Variables macroeconomicas BCRP. |
| `fact_sbs_financial_system.csv` | KPIs del sistema financiero SBS. |
| `fact_inei_pbi_department.csv` | PBI por departamento. |
| `fact_mef_state_enterprises.csv` | Empresas del Estado MEF. |
| `fact_bvl_market_snapshot.csv` | Snapshot BVL. |
| `source_coverage.csv` | Auditoria de fuentes oficiales. |
| `data_profile_tables.csv` | Perfilado por tabla. |
| `data_profile_columns.csv` | Perfilado por columna. |
| `data_quality_results.csv` | Resultado de reglas de calidad. |

## 8. KPIs financieros calculados

En la tabla `fact_financial_kpis.csv` se calculan:

| KPI | Formula |
|---|---|
| ROA | `utilidad_neta / activo_total` |
| ROE | `utilidad_neta / patrimonio_total` |
| Endeudamiento | `pasivo_total / activo_total` |
| Apalancamiento | `pasivo_total / patrimonio_total` |
| Margen neto | `utilidad_neta / total_ingreso` |
| Crecimiento de ingresos | Variacion interanual por empresa y periodo |
| Crecimiento de utilidad | Variacion interanual por empresa y periodo |
| Score de riesgo | Ponderacion de endeudamiento, ROA, margen y deterioro de utilidad |

## 9. Score de riesgo

El score de riesgo es un indicador academico de 0 a 100. Mientras mas alto, mayor riesgo financiero.

Componentes:

- Endeudamiento alto: hasta 35 puntos.
- ROA bajo o negativo: hasta 25 puntos.
- Margen neto bajo o negativo: hasta 20 puntos.
- Caida de utilidad: hasta 20 puntos.

Clasificacion:

| Nivel | Rango |
|---|---|
| Bajo | Menor a 40 |
| Medio | 40 a 69.99 |
| Alto | 70 o mas |

## 10. Data profiling

El proyecto genera perfilado automatico de tablas y columnas.

Archivos:

```text
data/gold/data_profile_tables.csv
data/gold/data_profile_columns.csv
```

Metricas incluidas:

- Numero de filas.
- Numero de columnas.
- Filas duplicadas.
- Celdas nulas.
- Porcentaje de nulos.
- Columnas numericas.
- Columnas de texto.
- Distintos por columna.
- Minimo, maximo y promedio para columnas numericas.

## 11. Calidad de datos

El archivo de reglas de calidad es:

```text
data/gold/data_quality_results.csv
```

Reglas implementadas:

- Las tablas gold principales tienen filas.
- La llave de empresa SMV no es nula.
- Los activos financieros son positivos o no negativos.
- El score de riesgo esta entre 0 y 100.
- Los anios INEI estan en rango esperado.
- Las seis fuentes oficiales tienen estado `ok`.

Resultado de la ultima ejecucion:

```text
12 checks ejecutados
12 checks aprobados
0 checks fallidos
```

## 12. Dashboard

El dashboard Streamlit se ejecuta con:

```powershell
streamlit run dashboard/app.py
```

URL local:

```text
http://localhost:8501
```

Vistas:

- Radar de riesgo.
- Analisis sectorial.
- Contexto macro BCRP.
- Fuentes externas: SBS, INEI, MEF y BVL.
- Calidad de datos.
- Cobertura de fuentes.
- Tabla gold.

## 13. Power BI

Para Power BI Desktop se preparo un paquete en:

```text
powerbi/
```

Incluye:

- Modelo recomendado.
- Medidas DAX.
- Power Query M para cargar las tablas gold.
- Instrucciones para construir las paginas del dashboard.

Power BI debe conectarse a los CSV generados en `data/gold/`.

## 14. Como ejecutar todo el pipeline

Desde la raiz del proyecto:

```powershell
pip install -r requirements.txt
python -m src.smv_bi.run_pipeline
streamlit run dashboard/app.py
```

El pipeline ejecuta:

1. Descarga bronze.
2. Transformacion silver.
3. Generacion gold.
4. Perfilado.
5. Reglas de calidad.
6. Actualizacion de datasets para dashboard.

## 15. Limitaciones y mejora futura

El proyecto ya integra las seis fuentes oficiales. La mejora principal seria ampliar BVL desde snapshot de boletin diario hacia historico completo de precios por nemonico, si se dispone de un endpoint historico estable o archivos descargables oficiales por accion.

Tambien se podria publicar el modelo en Power BI Service si se cuenta con licencia/cuenta institucional.

## 16. Conclusion

SMV 360 cumple con un flujo BI completo: fuentes oficiales, ingesta, limpieza, capa gold, KPIs, calidad de datos, perfilado y dashboards. El proyecto es reproducible porque todos los resultados se regeneran desde scripts y queda trazabilidad desde los datos crudos hasta los indicadores finales.
