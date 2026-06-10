# SMV 360 BI

Proyecto de Inteligencia de Negocios orientado al mercado de valores peruano.

El repositorio integra dos frentes:

- Diseno del Data Warehouse y scripts DDL para PostgreSQL.
- Pipeline real de datos abiertos SMV/BCRP con capas bronze, silver, gold y dashboard local.

## Estructura

```text
dashboard/
  app.py

data/
  bronze/
  silver/
  gold/

docs/
  data_catalog.md
  diccionario_datos.md
  fuentes.md
  mapeo_fuente_destino.md
  modelo_dimensional.md

sql/
  ddl/

src/
  smv_bi/
```

## Capas de datos

- `data/bronze`: respuestas crudas descargadas desde fuentes oficiales.
- `data/silver`: datos normalizados, limpios y listos para cruces.
- `data/gold`: tablas analiticas para dashboards y KPIs.
- `dashboard`: dashboard local en Streamlit.

## Fuentes iniciales

- SMV principales cuentas financieras: `https://mvnet.smv.gob.pe/ws_OD_EEFF/WebServiceInfoFinanciera.asmx/obtener_EFData`
- BCRP API de series estadisticas: `https://estadisticas.bcrp.gob.pe/estadisticas/series/api/`
- BVL boletin diario: `https://documents.bvl.com.pe/pubdif/boldia/bolres.htm`
- SBS datos abiertos: `https://www.sbs.gob.pe/estadisticas-y-publicaciones/estadisticas-/datos-abiertos_`
- INEI PBI Peru: `https://www.inei.gob.pe/media/MenuRecursivo/indices_tematicos/pbi_peru_16.xlsx`
- MEF / Datos Abiertos: `https://api.datosabiertos.mef.gob.pe/DatosAbiertos/v1/datastore_search`

## Ejecutar

```powershell
pip install -r requirements.txt
python -m src.smv_bi.run_pipeline
streamlit run dashboard/app.py
```

Dashboard local:

```text
http://localhost:8501
```

## Dashboard

La app Streamlit incluye cuatro vistas:

- Radar de riesgo.
- Analisis sectorial.
- Contexto macro BCRP.
- Fuentes externas: SBS, INEI, MEF y BVL.
- Calidad de datos y profiling.
- Cobertura de fuentes.
- Tabla gold exportable.

## Alcance actual

El pipeline descarga datos 2019-2024 de informacion financiera individual de la SMV, calcula ratios financieros, arma un score de riesgo y genera tablas gold para el dashboard.

El dashboard principal usa SMV + BCRP para el riesgo corporativo. Ademas, BVL, SBS, INEI y MEF se descargan, se transforman a silver/gold y se muestran como fuentes externas complementarias. La auditoria general queda en `data/gold/source_coverage.csv`.

## Calidad de datos

El pipeline genera:

- `data/gold/data_profile_tables.csv`
- `data/gold/data_profile_columns.csv`
- `data/gold/data_quality_results.csv`

Estos archivos permiten sustentar completitud, nulos, duplicados, tipos de datos y reglas minimas de validacion.

## Documentacion

- `docs/data_catalog.md`: catalogo de datasets, KPIs y score de riesgo.
- `docs/explicacion_profesor.md`: explicacion completa del proyecto para sustentacion.
- `docs/modelo_dimensional.md`: modelo dimensional propuesto.
- `docs/diccionario_datos.md`: diccionario preliminar del DW.
- `docs/fuentes.md`: fuentes oficiales.
- `docs/mapeo_fuente_destino.md`: mapeo fuente-destino.
- `powerbi/`: paquete para construir el dashboard en Power BI Desktop con medidas DAX, modelo y especificacion visual.
