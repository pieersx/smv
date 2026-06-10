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
- Tabla gold exportable.

## Alcance actual

El pipeline descarga datos 2019-2024 de informacion financiera individual de la SMV, calcula ratios financieros, arma un score de riesgo y genera tablas gold para el dashboard.

La BVL y SBS quedan como ampliacion recomendada despues de estabilizar esta primera version, porque SMV + BCRP ya cubren un caso BI completo y defendible.

## Documentacion

- `docs/data_catalog.md`: catalogo de datasets, KPIs y score de riesgo.
- `docs/modelo_dimensional.md`: modelo dimensional propuesto.
- `docs/diccionario_datos.md`: diccionario preliminar del DW.
- `docs/fuentes.md`: fuentes oficiales.
- `docs/mapeo_fuente_destino.md`: mapeo fuente-destino.
