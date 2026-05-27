# Modelo Dimensional

## Objetivo

Disenar un Data Warehouse orientado al analisis de riesgo financiero corporativo, comportamiento bursatil y contexto macroeconomico.

## Esquema elegido

Se utiliza un esquema estrella con tres tablas de hechos y tres dimensiones principales.

## Dimensiones

### dim_sector
- Normaliza la clasificacion sectorial de las empresas.

### dim_empresa
- Integra el identificador empresarial de SMV con los identificadores bursatiles de BVL.

### dim_fecha
- Provee una dimension de calendario comun para hechos financieros, bursatiles y macro.

## Hechos

### fact_indicadores_financieros
- Granularidad: empresa x fecha_reporte x tipo_estado
- Fuente principal: SMV
- Contiene cuentas financieras base y ratios derivados.

### fact_precios_bvl
- Granularidad: empresa x fecha_negociacion
- Fuente principal: BVL
- Contiene precios, volumenes y metricas bursatiles diarias.

### fact_macro
- Granularidad: fecha x indicador
- Fuente principal: BCRP / INEI
- Contiene series macroeconomicas en formato largo.

## Relaciones

1. `dim_sector 1 --- n dim_empresa`
2. `dim_empresa 1 --- n fact_indicadores_financieros`
3. `dim_empresa 1 --- n fact_precios_bvl`
4. `dim_fecha 1 --- n fact_indicadores_financieros`
5. `dim_fecha 1 --- n fact_precios_bvl`
6. `dim_fecha 1 --- n fact_macro`

## Granularidad por tabla

| Tabla | Granularidad |
|---|---|
| `dim_sector` | un registro por sector normalizado |
| `dim_empresa` | un registro por empresa |
| `dim_fecha` | un registro por fecha |
| `fact_indicadores_financieros` | empresa x fecha x tipo_estado |
| `fact_precios_bvl` | empresa x fecha |
| `fact_macro` | fecha x indicador |

## KPIs que soporta el modelo

- ROE
- ROA
- Current Ratio
- Deuda / EBITDA
- Altman Z-Score
- Precio de cierre
- Retorno diario
- Volumen negociado
- Tipo de cambio
- Inflacion
- Tasa de referencia

## Alcance de S8-S9

Este diseno deja lista la base tecnica para `S10`:

- ingestion de datasets
- limpieza y estandarizacion
- carga a PostgreSQL
- construccion del dashboard en Power BI
