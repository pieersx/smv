# Mapeo Fuente a Destino

## Objetivo

Este documento define el mapeo preliminar entre los datasets priorizados y las tablas destino del Data Warehouse. Sirve como puente entre el diseno dimensional de `S8-S9` y la implementacion ETL de `S10`.

## Convenciones

- `origen_columna`: nombre esperado o equivalente en la fuente original
- `destino_columna`: columna definida en el DW
- `transformacion`: regla esperada para homologar el dato
- `observaciones`: notas de calidad o cruce

## 1. SMV - Empresas inscritas

### Destino principal
- `dim_empresa`

| Fuente | origen_columna | destino_tabla | destino_columna | transformacion | observaciones |
|---|---|---|---|---|---|
| SMV Empresas | `RUC` | `dim_empresa` | `ruc` | trim, solo digitos, longitud 11 | clave natural principal |
| SMV Empresas | `Razon Social` | `dim_empresa` | `razon_social` | trim, uppercase opcional para matching | nombre legal base |
| SMV Empresas | `Sector` | `dim_empresa` | `sector_smv` | trim | sector original SMV |
| SMV Empresas | `Fecha Inscripcion` | `dim_empresa` | `fecha_inscripcion_smv` | parse a date | puede venir vacio |
| SMV Empresas | `Estado` | `dim_empresa` | `estado_registro` | trim | estado en registro |
| SMV Empresas | constante `SMV` | `dim_empresa` | `origen_empresa` | literal | indica fuente principal |

### Destino secundario
- `dim_sector`

| Fuente | origen_columna | destino_tabla | destino_columna | transformacion | observaciones |
|---|---|---|---|---|---|
| SMV Empresas | `Sector` | `dim_sector` | `sector_nombre` | trim, catalogar y deduplicar | puede necesitar homologacion con BVL |
| SMV Empresas | constante `SMV` | `dim_sector` | `clasificacion_fuente` | literal | clasificacion de origen |

## 2. SMV - Estado de Situacion Financiera

### Destino principal
- `fact_indicadores_financieros`

| Fuente | origen_columna | destino_tabla | destino_columna | transformacion | observaciones |
|---|---|---|---|---|---|
| SMV Balance | `RUC` o identificador empresa | `fact_indicadores_financieros` | `empresa_key` | lookup contra `dim_empresa` | requiere cruce previo |
| SMV Balance | `Fecha` / `Periodo` | `fact_indicadores_financieros` | `fecha_key` | construir `yyyymmdd` y lookup contra `dim_fecha` | usar fecha de cierre |
| SMV Balance | `Tipo Estado` | `fact_indicadores_financieros` | `tipo_estado` | mapear a `individual` o `consolidado` | obligatorio |
| SMV Balance | `Frecuencia` / `Periodo` | `fact_indicadores_financieros` | `frecuencia_reporte` | mapear a `trimestral` o `anual` | obligatorio |
| SMV Balance | `Moneda` | `fact_indicadores_financieros` | `moneda` | trim, uppercase | PEN o USD, etc. |
| SMV Balance | `Activo Total` | `fact_indicadores_financieros` | `activo_total` | decimal | cuenta base |
| SMV Balance | `Activo Corriente` | `fact_indicadores_financieros` | `activo_corriente` | decimal | cuenta base |
| SMV Balance | `Pasivo Total` | `fact_indicadores_financieros` | `pasivo_total` | decimal | cuenta base |
| SMV Balance | `Pasivo Corriente` | `fact_indicadores_financieros` | `pasivo_corriente` | decimal | cuenta base |
| SMV Balance | `Patrimonio Neto` | `fact_indicadores_financieros` | `patrimonio_neto` | decimal | cuenta base |
| SMV Balance | derivado | `fact_indicadores_financieros` | `capital_trabajo` | `activo_corriente - pasivo_corriente` | derivado DW |

## 3. SMV - Estado de Resultados

### Destino principal
- `fact_indicadores_financieros`

| Fuente | origen_columna | destino_tabla | destino_columna | transformacion | observaciones |
|---|---|---|---|---|---|
| SMV Resultados | `RUC` o identificador empresa | `fact_indicadores_financieros` | `empresa_key` | lookup contra `dim_empresa` | debe coincidir con balance |
| SMV Resultados | `Fecha` / `Periodo` | `fact_indicadores_financieros` | `fecha_key` | lookup contra `dim_fecha` | usar mismo corte |
| SMV Resultados | `Ventas Netas` / `Ingresos` | `fact_indicadores_financieros` | `ventas_netas` | decimal | posible alias por fuente |
| SMV Resultados | `Utilidad Operativa` | `fact_indicadores_financieros` | `utilidad_operativa` | decimal | cuenta base |
| SMV Resultados | `Utilidad Neta` | `fact_indicadores_financieros` | `utilidad_neta` | decimal | cuenta base |
| SMV Resultados | `EBITDA` si existe | `fact_indicadores_financieros` | `ebitda` | decimal | nullable |
| SMV Resultados | `Utilidades Retenidas` si existe | `fact_indicadores_financieros` | `utilidades_retenidas` | decimal | puede venir de otra estructura |
| SMV Resultados | derivado | `fact_indicadores_financieros` | `roe` | `utilidad_neta / patrimonio_neto` | calculado posterior |
| SMV Resultados | derivado | `fact_indicadores_financieros` | `roa` | `utilidad_neta / activo_total` | calculado posterior |
| SMV Resultados | derivado | `fact_indicadores_financieros` | `current_ratio` | `activo_corriente / pasivo_corriente` | calculado posterior |
| SMV Resultados | derivado | `fact_indicadores_financieros` | `deuda_ebitda` | `deuda_financiera_total / ebitda` | calculado posterior |
| SMV Resultados | derivado | `fact_indicadores_financieros` | `altman_z_score` | formula definida por negocio | calculado posterior |

## 4. BVL - Emisores

### Destino principal
- `dim_empresa`

| Fuente | origen_columna | destino_tabla | destino_columna | transformacion | observaciones |
|---|---|---|---|---|---|
| BVL Issuers | `companyCode` | `dim_empresa` | `company_code_bvl` | cast a string | identificador tecnico BVL |
| BVL Issuers | `companyName` | `dim_empresa` | `razon_social` | trim | usar para matching con SMV |
| BVL Issuers | `sectorCode` | `dim_sector` | `sector_codigo` | trim | catalogo tecnico BVL |
| BVL Issuers | `description` | `dim_sector` | `sector_nombre` | trim | suele ser descripcion sectorial |
| BVL Issuers | `subSectorCode` | `dim_empresa` | `subsector_bvl` | trim o lookup | puede requerir catalogo adicional |
| BVL Issuers | `website` | `dim_empresa` | `sitio_web` | trim | opcional |
| BVL Issuers | constante `TRUE` | `dim_empresa` | `es_emisora_bvl` | literal | marca emisora bursatil |

## 5. BVL - Codificacion / ISIN

### Destino principal
- `dim_empresa`

| Fuente | origen_columna | destino_tabla | destino_columna | transformacion | observaciones |
|---|---|---|---|---|---|
| BVL ISIN | `nemonico` | `dim_empresa` | `nemonico` | trim, uppercase | clave bursatil de cruce |
| BVL ISIN | `isin` | `dim_empresa` | `isin` | trim, uppercase | identificador internacional |
| BVL ISIN | `businnesName` | `dim_empresa` | `razon_social` | trim | util para matching adicional |

## 6. BVL - Precios historicos por accion

### Destino principal
- `fact_precios_bvl`

| Fuente | origen_columna | destino_tabla | destino_columna | transformacion | observaciones |
|---|---|---|---|---|---|
| BVL Prices | `nemonico` | `fact_precios_bvl` | `empresa_key` | lookup por `nemonico` en `dim_empresa` | clave de integracion |
| BVL Prices | `date` | `fact_precios_bvl` | `fecha_key` | parse date y lookup `dim_fecha` | obligatorio |
| BVL Prices | `open` | `fact_precios_bvl` | `precio_apertura` | decimal | puede venir null |
| BVL Prices | `close` | `fact_precios_bvl` | `precio_cierre` | decimal | cuenta principal |
| BVL Prices | `high` | `fact_precios_bvl` | `precio_maximo` | decimal | |
| BVL Prices | `low` | `fact_precios_bvl` | `precio_minimo` | decimal | |
| BVL Prices | `average` | `fact_precios_bvl` | `precio_promedio` | decimal | |
| BVL Prices | `yesterday` o `yesterdayClose` | `fact_precios_bvl` | `precio_anterior` | decimal | depende del endpoint |
| BVL Prices | `quantityNegotiated` | `fact_precios_bvl` | `cantidad_negociada` | decimal | volumen |
| BVL Prices | `solAmountNegotiated` | `fact_precios_bvl` | `monto_negociado_pen` | decimal | soles |
| BVL Prices | `dollarAmountNegotiated` | `fact_precios_bvl` | `monto_negociado_usd` | decimal | dolares |
| BVL Prices | `currencySymbol` | `fact_precios_bvl` | `moneda` | trim | moneda del instrumento |
| BVL Prices | derivado | `fact_precios_bvl` | `variacion_pct` | `(precio_cierre / precio_anterior) - 1` | calculado DW |
| BVL Prices | derivado | `fact_precios_bvl` | `retorno_diario` | igual que variacion o log-return | definir regla unica |

## 7. BVL - Mercado diario / resumen mercado

### Destino principal
- `fact_precios_bvl`

| Fuente | origen_columna | destino_tabla | destino_columna | transformacion | observaciones |
|---|---|---|---|---|---|
| BVL Market | `operationsNumber` o `numNeg` | `fact_precios_bvl` | `numero_operaciones` | integer | puede complementar historico |
| BVL Market | `percentageChange` | `fact_precios_bvl` | `variacion_pct` | decimal | usar solo si historico no lo trae |

## 8. BCRP - Tipo de cambio

### Destino principal
- `fact_macro`

| Fuente | origen_columna | destino_tabla | destino_columna | transformacion | observaciones |
|---|---|---|---|---|---|
| BCRP | `fecha` | `fact_macro` | `fecha_key` | parse date y lookup `dim_fecha` | obligatorio |
| BCRP | codigo serie | `fact_macro` | `indicador_codigo` | literal del API/export | congelar codigo al implementar |
| BCRP | nombre serie | `fact_macro` | `indicador_nombre` | trim | ejemplo: tipo de cambio |
| BCRP | constante `BCRP` | `fact_macro` | `fuente` | literal | |
| BCRP | frecuencia serie | `fact_macro` | `frecuencia` | mapear a diaria o mensual | |
| BCRP | unidad | `fact_macro` | `unidad_medida` | trim | `PEN/USD` u otra |
| BCRP | `valor` | `fact_macro` | `valor` | decimal | |

## 9. BCRP - Inflacion

### Destino principal
- `fact_macro`

| Fuente | origen_columna | destino_tabla | destino_columna | transformacion | observaciones |
|---|---|---|---|---|---|
| BCRP | `fecha` | `fact_macro` | `fecha_key` | lookup contra `dim_fecha` | usar fecha de periodo |
| BCRP | codigo serie IPC | `fact_macro` | `indicador_codigo` | literal | validar codigo en BCRPData |
| BCRP | nombre serie | `fact_macro` | `indicador_nombre` | trim | inflacion o IPC |
| BCRP | constante `BCRP` | `fact_macro` | `fuente` | literal | |
| BCRP | frecuencia | `fact_macro` | `frecuencia` | mensual | |
| BCRP | unidad | `fact_macro` | `unidad_medida` | porcentaje o indice | |
| BCRP | `valor` | `fact_macro` | `valor` | decimal | |

## 10. BCRP - Tasa de referencia

### Destino principal
- `fact_macro`

| Fuente | origen_columna | destino_tabla | destino_columna | transformacion | observaciones |
|---|---|---|---|---|---|
| BCRP | `fecha` | `fact_macro` | `fecha_key` | lookup contra `dim_fecha` | |
| BCRP | codigo serie tasa | `fact_macro` | `indicador_codigo` | literal | validar codigo definitivo |
| BCRP | nombre serie | `fact_macro` | `indicador_nombre` | trim | tasa de referencia |
| BCRP | constante `BCRP` | `fact_macro` | `fuente` | literal | |
| BCRP | frecuencia | `fact_macro` | `frecuencia` | diaria o mensual segun serie elegida | definir una sola para el MVP |
| BCRP | unidad | `fact_macro` | `unidad_medida` | porcentaje | |
| BCRP | `valor` | `fact_macro` | `valor` | decimal | |

## 11. BCRP - Cotizaciones internacionales

### Destino principal
- `fact_macro`

| Fuente | origen_columna | destino_tabla | destino_columna | transformacion | observaciones |
|---|---|---|---|---|---|
| BCRP | `fecha` | `fact_macro` | `fecha_key` | lookup contra `dim_fecha` | |
| BCRP | codigo serie cobre/oro/zinc | `fact_macro` | `indicador_codigo` | literal | una fila por indicador |
| BCRP | nombre serie | `fact_macro` | `indicador_nombre` | trim | commodity especifico |
| BCRP | constante `BCRP` | `fact_macro` | `fuente` | literal | |
| BCRP | frecuencia | `fact_macro` | `frecuencia` | diaria | |
| BCRP | unidad | `fact_macro` | `unidad_medida` | USD u otra | |
| BCRP | `valor` | `fact_macro` | `valor` | decimal | |

## 12. INEI - PBI sectorial

### Destino principal
- `fact_macro`

| Fuente | origen_columna | destino_tabla | destino_columna | transformacion | observaciones |
|---|---|---|---|---|---|
| INEI PBI | `fecha` / `anio` / `trimestre` | `fact_macro` | `fecha_key` | estandarizar a fecha de cierre de periodo | definir regla uniforme |
| INEI PBI | codigo o nivel sectorial | `fact_macro` | `indicador_codigo` | prefijar con `INEI_` si no existe codigo nativo | |
| INEI PBI | nombre actividad | `fact_macro` | `indicador_nombre` | trim | ejemplo: mineria e hidrocarburos |
| INEI PBI | constante `INEI` | `fact_macro` | `fuente` | literal | |
| INEI PBI | frecuencia | `fact_macro` | `frecuencia` | trimestral o anual | elegir una serie principal |
| INEI PBI | unidad | `fact_macro` | `unidad_medida` | indice, millones, variacion, etc. | documentar al implementar |
| INEI PBI | `valor` | `fact_macro` | `valor` | decimal | |

## Reglas de integracion clave

### Empresa
1. Prioridad de cruce: `RUC` -> `nemonico` -> `company_code_bvl` -> `razon_social`
2. `dim_empresa` debe quedar como maestro consolidado entre SMV y BVL.

### Fecha
1. Toda fecha debe resolverse a `fecha_key` en formato `yyyymmdd`.
2. Para series mensuales o trimestrales se debe definir una fecha de representacion consistente.

### Sector
1. Mantener sector original de `SMV` y `BVL`.
2. `dim_sector` sera la version normalizada para analisis.

## Pendientes para S10

1. Congelar nombres reales de columnas por archivo descargado.
2. Validar codigos exactos de series BCRP.
3. Definir catalogo de homologacion de sectores.
4. Definir criterio final para `ebitda`, `deuda_financiera_total` y `altman_z_score`.
