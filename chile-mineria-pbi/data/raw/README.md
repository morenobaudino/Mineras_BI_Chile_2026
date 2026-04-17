# `data/raw`

Coloca aquí los archivos **sin editar** descargados de sitios oficiales o IR.

## Convención de nombres

`YYYY[_Qq]_EMISOR_descripcion.ext`

Ejemplos:

- `2024Q1_BHP_results.pdf`
- `2023_CODELCO_memoria.pdf`
- `2024Q2_ESCONDIDA_supplement.xlsx` (si aplica)

## Registro de ingesta

Desde la raíz del proyecto (con el entorno virtual activado si usas uno):

`python -m src.etl.register_raw --entity CODELCO`

El hash SHA-256 se guarda en `ingest_manifest.csv` y, si ya existe la base `data/mineria_chile.db`, también en `stg_ingest_log`.
