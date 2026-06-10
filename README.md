# SMV 360 BI

Proyecto BI para construir un dashboard de riesgo financiero corporativo usando datos abiertos oficiales de la SMV y series macroeconomicas del BCRP.

## Capas

- `data/bronze`: respuestas crudas descargadas desde fuentes oficiales.
- `data/silver`: datos normalizados, limpios y listos para cruces.
- `data/gold`: tablas analiticas para dashboards y KPIs.
- `dashboard`: dashboard local en Streamlit.

## Fuentes iniciales

- SMV principales cuentas financieras: `https://mvnet.smv.gob.pe/ws_OD_EEFF/WebServiceInfoFinanciera.asmx/obtener_EFData`
- BCRP API de series estadisticas: `https://estadisticas.bcrp.gob.pe/estadisticas/series/api/`

## Ejecutar

```powershell
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

## Documentacion

Ver `docs/data_catalog.md` para el catalogo de datasets, KPIs y definicion del score de riesgo.

## Alcance actual

El pipeline descarga 2019-2024 para informacion financiera individual de la SMV, calcula ratios financieros, arma un score de riesgo y genera tablas gold para el dashboard.

La BVL y SBS quedan como ampliacion recomendada despues de estabilizar la primera version, porque SMV + BCRP ya cubren un caso BI completo y defendible.
