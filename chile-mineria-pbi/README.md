# Chile minería — Python + SQL + Power BI

Proyecto base para **Codelco** y **Minera Escondida (vía reportes BHP)**: ingesta manual de archivos públicos/IR, modelo estrella en **MySQL** (con fallback SQLite), ETL en **Python** y consumo en **Power BI**.

## Requisitos

- Python 3.11+ (probado con 3.13)
- Power BI Desktop (para informes)

## Instalación

```powershell
cd "c:\Users\MORELBA BAUDINO\Desktop\proyectos_cursor\chile-mineria-pbi"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configurar base MySQL

Define la variable de entorno `DATABASE_URL` antes de ejecutar scripts:

```powershell
$env:DATABASE_URL = "mysql+pymysql://root:TU_PASSWORD@localhost:3306/chile_mineria_pbi?charset=utf8mb4"
```

Nota: MySQL Workbench es el cliente visual; la URL apunta al servidor MySQL.

## Crear / actualizar la base y datos demo

Aplica el esquema y vistas del motor detectado (`sql/schema.mysql.sql` y `sql/views.mysql.sql` para MySQL), y carga **datos ilustrativos** (2024 T1 y T2) para cablear Power BI:

```powershell
python -m src.etl.load_db --seed
```

Si no defines `DATABASE_URL`, usa SQLite en `data/mineria_chile.db`. Vuelve a ejecutar el mismo comando para **refrescar** las filas demo sin duplicarlas.

## Registrar archivos en `data/raw`

```powershell
python -m src.etl.register_raw --entity CODELCO
```

Ver [data/raw/README.md](data/raw/README.md).

## Exportar vistas a CSV (Power BI)

```powershell
python -m src.etl.export_views_csv
```

Archivos en `data/processed/pbi_export/` (UTF-8 con BOM).

## Estructura

| Ruta | Uso |
|------|-----|
| [sql/schema.sql](sql/schema.sql) | Tablas `dim_*`, `fact_*`, `stg_ingest_log` |
| [sql/schema.mysql.sql](sql/schema.mysql.sql) | Tablas para MySQL |
| [sql/views.sql](sql/views.sql) | Vistas listas para PBI |
| [sql/views.mysql.sql](sql/views.mysql.sql) | Vistas para MySQL |
| [src/config/entities.yaml](src/config/entities.yaml) | Catálogo fijo Codelco + Escondida/BHP |
| [src/etl/extract_tables.py](src/etl/extract_tables.py) | Lectura de Excel/CSV/PDF (tablas) |
| [src/etl/transform_metrics.py](src/etl/transform_metrics.py) | Utilidades (p. ej. fechas de trimestre) |
| [src/etl/load_db.py](src/etl/load_db.py) | Aplicar SQL + semilla demo |
| [src/etl/register_raw.py](src/etl/register_raw.py) | Manifest + hash de `data/raw` |
| [src/etl/export_views_csv.py](src/etl/export_views_csv.py) | Export para Power BI |
| [docs/powerbi.md](docs/powerbi.md) | Conexión ODBC/CSV y DAX sugerido |

## Nota sobre datos demo

Las filas con `source_file = SEED_DEMO` son **placeholders** para validar el flujo. Sustitúyelas por valores extraídos de memorias Codelco y reportes BHP usando `extract_tables.py` y nuevas rutas en `load_db` o scripts dedicados.


