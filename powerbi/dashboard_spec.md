# Especificacion de dashboards Power BI - SMV 360

## Pagina 1: Radar de riesgo corporativo

Visuales:

- Cards:
  - Empresas
  - Score Riesgo Promedio
  - Empresas Riesgo Alto
  - Activo Total
- Barras horizontales:
  - `nombre_empresa`
  - `score_riesgo`
  - filtro Top N = 20
- Dona:
  - `nivel_riesgo`
  - conteo de empresas
- Scatter:
  - X: `endeudamiento`
  - Y: `roa`
  - size: `activo_total`
  - legend: `nivel_riesgo`

Filtros:

- `periodo_label`
- `tipo_sector`

## Pagina 2: Analisis sectorial

Visuales:

- Barras:
  - `tipo_sector`
  - `score_riesgo_promedio`
- Scatter:
  - X: `endeudamiento_promedio`
  - Y: `roa_promedio`
  - size: `empresas`
- Tabla:
  - sector
  - empresas
  - activo_total
  - pasivo_total
  - utilidad_neta

## Pagina 3: Contexto macro BCRP

Visuales:

- Line chart:
  - fecha
  - tipo de cambio
  - tasa de referencia
  - cobre
  - oro
  - IPC
- Line chart anual:
  - score de riesgo promedio por ejercicio
  - tipo de cambio promedio
  - tasa promedio

## Pagina 4: Fuentes externas

Visuales SBS:

- Card: entidades SBS.
- Card: activos SBS.
- Card: ratio atrasados SBS.
- Barras: entidades por `total_activo`.

Visuales INEI:

- Barras: `departamento` por `pbi_miles_soles_2007`.
- Color: `variacion_pbi`.

Visuales MEF:

- Barras: departamento por `monto_total`.
- Tabla: entidad, rubro, monto.

Visuales BVL:

- Tabla: categoria, nombre, valores extraidos del boletin.

## Pagina 5: Calidad de datos

Visuales:

- Card: Checks Calidad.
- Card: Checks OK.
- Card: Checks Fallidos.
- Tabla: `data_quality_results`.
- Tabla: `data_profile_tables`.

## Pagina 6: Cobertura de fuentes

Visuales:

- Card: Fuentes Verificadas.
- Tabla: source, dataset, records, status, url.
- Barras: registros por fuente.
