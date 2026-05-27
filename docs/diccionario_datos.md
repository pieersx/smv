# Diccionario de Datos Preliminar

## dim_sector

| Campo | Tipo | Nulo | PK | FK | Descripcion | Origen |
|---|---|---|---|---|---|---|
| `sector_key` | `bigserial` | No | Si | No | Identificador sustituto del sector | DW |
| `sector_codigo` | `varchar(50)` | Si | No | No | Codigo sectorial de negocio | SMV / BVL |
| `sector_nombre` | `varchar(150)` | No | No | No | Nombre normalizado del sector | SMV / BVL |
| `subsector_nombre` | `varchar(150)` | Si | No | No | Nombre del subsector | BVL |
| `clasificacion_fuente` | `varchar(50)` | Si | No | No | Fuente de la clasificacion | DW |
| `descripcion` | `varchar(255)` | Si | No | No | Descripcion complementaria | DW |

## dim_empresa

| Campo | Tipo | Nulo | PK | FK | Descripcion | Origen |
|---|---|---|---|---|---|---|
| `empresa_key` | `bigserial` | No | Si | No | Identificador sustituto de empresa | DW |
| `ruc` | `varchar(11)` | Si | No | No | RUC de la empresa | SMV |
| `razon_social` | `varchar(255)` | No | No | No | Nombre legal de la empresa | SMV / BVL |
| `company_code_bvl` | `varchar(50)` | Si | No | No | Identificador interno del emisor en BVL | BVL |
| `nemonico` | `varchar(50)` | Si | No | No | Codigo bursatil del valor principal | BVL |
| `isin` | `varchar(50)` | Si | No | No | Codigo ISIN del valor | BVL |
| `sector_key` | `bigint` | Si | No | Si | Referencia al sector normalizado | DW |
| `sector_smv` | `varchar(150)` | Si | No | No | Sector reportado por SMV | SMV |
| `sector_bvl` | `varchar(150)` | Si | No | No | Sector reportado por BVL | BVL |
| `subsector_bvl` | `varchar(150)` | Si | No | No | Subsector reportado por BVL | BVL |
| `fecha_inscripcion_smv` | `date` | Si | No | No | Fecha de inscripcion en SMV | SMV |
| `estado_registro` | `varchar(50)` | Si | No | No | Estado de la empresa en la fuente | SMV |
| `origen_empresa` | `varchar(50)` | Si | No | No | Fuente principal del maestro | DW |
| `es_emisora_bvl` | `boolean` | No | No | No | Indica si tiene presencia bursatil | DW |
| `sitio_web` | `varchar(255)` | Si | No | No | Sitio web corporativo | BVL |

## dim_fecha

| Campo | Tipo | Nulo | PK | FK | Descripcion | Origen |
|---|---|---|---|---|---|---|
| `fecha_key` | `integer` | No | Si | No | Clave de fecha en formato yyyymmdd | DW |
| `fecha` | `date` | No | No | No | Fecha calendario | DW |
| `anio` | `smallint` | No | No | No | Ano de la fecha | DW |
| `trimestre` | `smallint` | No | No | No | Trimestre calendario | DW |
| `mes` | `smallint` | No | No | No | Mes calendario | DW |
| `nombre_mes` | `varchar(20)` | No | No | No | Nombre del mes | DW |
| `semana_anio` | `smallint` | No | No | No | Semana del ano | DW |
| `dia_mes` | `smallint` | No | No | No | Dia del mes | DW |
| `dia_semana` | `smallint` | No | No | No | Dia de la semana numerico | DW |
| `nombre_dia` | `varchar(20)` | No | No | No | Nombre del dia | DW |
| `es_fin_mes` | `boolean` | No | No | No | Marca ultimo dia del mes | DW |
| `es_dia_habil` | `boolean` | No | No | No | Marca dia habil general | DW |

## fact_indicadores_financieros

| Campo | Tipo | Nulo | PK | FK | Descripcion | Origen |
|---|---|---|---|---|---|---|
| `fact_financiero_key` | `bigserial` | No | Si | No | Identificador del hecho financiero | DW |
| `empresa_key` | `bigint` | No | No | Si | Referencia a empresa | DW |
| `fecha_key` | `integer` | No | No | Si | Referencia a fecha | DW |
| `tipo_estado` | `varchar(20)` | No | No | No | Individual o consolidado | SMV |
| `frecuencia_reporte` | `varchar(20)` | No | No | No | Trimestral o anual | SMV |
| `moneda` | `varchar(10)` | Si | No | No | Moneda del reporte | SMV |
| `fuente` | `varchar(20)` | No | No | No | Fuente del dato | DW |
| `activo_total` | `numeric(18,2)` | Si | No | No | Activo total | SMV |
| `activo_corriente` | `numeric(18,2)` | Si | No | No | Activo corriente | SMV |
| `pasivo_total` | `numeric(18,2)` | Si | No | No | Pasivo total | SMV |
| `pasivo_corriente` | `numeric(18,2)` | Si | No | No | Pasivo corriente | SMV |
| `patrimonio_neto` | `numeric(18,2)` | Si | No | No | Patrimonio neto | SMV |
| `ventas_netas` | `numeric(18,2)` | Si | No | No | Ingresos o ventas netas | SMV |
| `utilidad_operativa` | `numeric(18,2)` | Si | No | No | Resultado operativo | SMV |
| `utilidad_neta` | `numeric(18,2)` | Si | No | No | Resultado neto | SMV |
| `ebitda` | `numeric(18,2)` | Si | No | No | EBITDA calculado o reportado | DW / SMV |
| `deuda_financiera_total` | `numeric(18,2)` | Si | No | No | Deuda financiera total | DW / SMV |
| `capital_trabajo` | `numeric(18,2)` | Si | No | No | Activo corriente menos pasivo corriente | DW |
| `utilidades_retenidas` | `numeric(18,2)` | Si | No | No | Utilidades retenidas | SMV |
| `roe` | `numeric(10,4)` | Si | No | No | Utilidad neta / patrimonio neto | DW |
| `roa` | `numeric(10,4)` | Si | No | No | Utilidad neta / activo total | DW |
| `current_ratio` | `numeric(10,4)` | Si | No | No | Activo corriente / pasivo corriente | DW |
| `deuda_ebitda` | `numeric(10,4)` | Si | No | No | Deuda financiera / EBITDA | DW |
| `altman_z_score` | `numeric(10,4)` | Si | No | No | Score de riesgo financiero | DW |

## fact_precios_bvl

| Campo | Tipo | Nulo | PK | FK | Descripcion | Origen |
|---|---|---|---|---|---|---|
| `fact_precio_key` | `bigserial` | No | Si | No | Identificador del hecho bursatil | DW |
| `empresa_key` | `bigint` | No | No | Si | Referencia a empresa | DW |
| `fecha_key` | `integer` | No | No | Si | Referencia a fecha | DW |
| `precio_apertura` | `numeric(18,4)` | Si | No | No | Precio de apertura | BVL |
| `precio_cierre` | `numeric(18,4)` | Si | No | No | Precio de cierre | BVL |
| `precio_maximo` | `numeric(18,4)` | Si | No | No | Precio maximo diario | BVL |
| `precio_minimo` | `numeric(18,4)` | Si | No | No | Precio minimo diario | BVL |
| `precio_promedio` | `numeric(18,4)` | Si | No | No | Precio promedio | BVL |
| `precio_anterior` | `numeric(18,4)` | Si | No | No | Precio del dia anterior | BVL |
| `variacion_pct` | `numeric(10,4)` | Si | No | No | Variacion porcentual diaria | BVL / DW |
| `cantidad_negociada` | `numeric(18,4)` | Si | No | No | Cantidad negociada | BVL |
| `monto_negociado_pen` | `numeric(18,2)` | Si | No | No | Monto negociado en soles | BVL |
| `monto_negociado_usd` | `numeric(18,2)` | Si | No | No | Monto negociado en dolares | BVL |
| `numero_operaciones` | `integer` | Si | No | No | Numero de operaciones | BVL |
| `moneda` | `varchar(10)` | Si | No | No | Moneda del instrumento | BVL |
| `retorno_diario` | `numeric(10,6)` | Si | No | No | Retorno diario calculado | DW |
| `volatilidad_30d` | `numeric(10,6)` | Si | No | No | Volatilidad movil de 30 dias | DW |
| `beta_30d` | `numeric(10,6)` | Si | No | No | Beta movil de 30 dias | DW |

## fact_macro

| Campo | Tipo | Nulo | PK | FK | Descripcion | Origen |
|---|---|---|---|---|---|---|
| `fact_macro_key` | `bigserial` | No | Si | No | Identificador del hecho macro | DW |
| `fecha_key` | `integer` | No | No | Si | Referencia a fecha | DW |
| `indicador_codigo` | `varchar(50)` | No | No | No | Codigo de la serie o indicador | BCRP / INEI |
| `indicador_nombre` | `varchar(150)` | No | No | No | Nombre del indicador | BCRP / INEI |
| `fuente` | `varchar(20)` | No | No | No | Fuente del indicador | BCRP / INEI |
| `frecuencia` | `varchar(20)` | No | No | No | Frecuencia de la serie | BCRP / INEI |
| `unidad_medida` | `varchar(50)` | Si | No | No | Unidad de la serie | BCRP / INEI |
| `valor` | `numeric(18,6)` | No | No | No | Valor observado para la fecha | BCRP / INEI |
