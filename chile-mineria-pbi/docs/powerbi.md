# Power BI: conexión y medidas sugeridas

## Opción A — CSV (más simple)

1. Desde la raíz del proyecto:

   `python -m src.etl.export_views_csv`

2. En Power BI Desktop: **Obtener datos** → **Texto/CSV** y carga los archivos en `data/processed/pbi_export/` (UTF-8 con BOM para Excel).

3. Modelo: relaciona tablas si combinas varias vistas usando `entidad_codigo`, `anio`, `trimestre` como claves lógicas (o crea tablas de dimensión duplicadas desde las mismas vistas y normaliza).

## Opción B — MySQL (recomendada)

1. En Power BI: **Obtener datos** → **MySQL database** (o **ODBC** si prefieres DSN).
2. Conecta al servidor MySQL que usas en Workbench (host, puerto, base `chile_mineria_pbi`).
3. Selecciona vistas `vw_produccion_trimestral`, `vw_financiero_trimestral`, `vw_glosario_metricas`.

## Opción C — SQLite vía ODBC (fallback)

1. Instala un controlador ODBC para SQLite (por ejemplo el distribuido en [sqlite.org/odbc](https://www.sqlite.org/odbc.html)).
2. En Power BI: **Obtener datos** → **ODBC** → apunta al DSN o cadena que referencia `data/mineria_chile.db`.

## Medidas DAX de ejemplo

Ajusta nombres de tabla/columna al nombre que Power BI asigne al importar.

```dax
Prod Cu (kt) := SUM ( vw_produccion_trimestral[valor] )
```

```dax
EBITDA (USD m) := SUM ( vw_financiero_trimestral[valor] )
```

```dax
YoY EBITDA :=
VAR cy = [EBITDA (USD m)]
VAR py = CALCULATE ( [EBITDA (USD m)], SAMEPERIODLASTYEAR ( dim_tiempo[periodo_inicio] ) )
RETURN DIVIDE ( cy - py, py )
```

Si no usas una tabla calendario formal, calcula YoY con filtros explícitos en `anio` y `trimestre` en lugar de time intelligence estándar.

## Páginas del informe (recomendación)

- **Productividad**: gráficos por `entidad` y tiempo sobre `cu_production_kt` (y costos si cargas `c1_cost_usd_lb`).
- **Rentabilidad**: `ebitda_usd_m`, `net_income_usd_m`; página de **glosario** leyendo `vw_glosario_metricas` o una tabla fija con definiciones.

Los valores con `source_file = SEED_DEMO` son **ilustrativos**; sustitúyelos por cifras extraídas de memorias / resultados BHP y Codelco.
