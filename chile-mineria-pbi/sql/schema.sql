PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dim_tiempo (
  tiempo_id INTEGER PRIMARY KEY AUTOINCREMENT,
  periodo_inicio DATE NOT NULL,
  periodo_fin DATE NOT NULL,
  anio INTEGER NOT NULL,
  trimestre INTEGER,
  mes INTEGER,
  granularidad TEXT NOT NULL CHECK (granularidad IN ('day', 'month', 'quarter', 'year')),
  UNIQUE (periodo_inicio, periodo_fin, granularidad)
);

CREATE TABLE IF NOT EXISTS dim_entidad (
  entidad_id INTEGER PRIMARY KEY AUTOINCREMENT,
  codigo TEXT NOT NULL UNIQUE,
  nombre_mostrar TEXT NOT NULL,
  holding TEXT,
  tipo TEXT,
  pais TEXT NOT NULL DEFAULT 'CL',
  es_jv INTEGER NOT NULL DEFAULT 0 CHECK (es_jv IN (0, 1)),
  pct_participacion REAL,
  notas TEXT
);

CREATE TABLE IF NOT EXISTS dim_metrica (
  metrica_id INTEGER PRIMARY KEY AUTOINCREMENT,
  codigo TEXT NOT NULL UNIQUE,
  nombre TEXT NOT NULL,
  unidad TEXT,
  definicion TEXT,
  categoria TEXT NOT NULL CHECK (categoria IN ('produccion', 'finanzas', 'costo', 'otro'))
);

CREATE TABLE IF NOT EXISTS fact_produccion (
  fact_prod_id INTEGER PRIMARY KEY AUTOINCREMENT,
  tiempo_id INTEGER NOT NULL REFERENCES dim_tiempo (tiempo_id),
  entidad_id INTEGER NOT NULL REFERENCES dim_entidad (entidad_id),
  metrica_id INTEGER NOT NULL REFERENCES dim_metrica (metrica_id),
  valor REAL NOT NULL,
  granularidad TEXT NOT NULL,
  source_file TEXT,
  source_page TEXT,
  extracted_at TEXT NOT NULL DEFAULT (datetime('now')),
  notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_fact_prod_tiempo ON fact_produccion (tiempo_id);
CREATE INDEX IF NOT EXISTS idx_fact_prod_entidad ON fact_produccion (entidad_id);

CREATE TABLE IF NOT EXISTS fact_financiero (
  fact_fin_id INTEGER PRIMARY KEY AUTOINCREMENT,
  tiempo_id INTEGER NOT NULL REFERENCES dim_tiempo (tiempo_id),
  entidad_id INTEGER NOT NULL REFERENCES dim_entidad (entidad_id),
  metrica_id INTEGER NOT NULL REFERENCES dim_metrica (metrica_id),
  valor REAL NOT NULL,
  moneda TEXT NOT NULL DEFAULT 'USD',
  fx_a_usd REAL,
  granularidad TEXT NOT NULL,
  source_file TEXT,
  source_page TEXT,
  extracted_at TEXT NOT NULL DEFAULT (datetime('now')),
  notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_fact_fin_tiempo ON fact_financiero (tiempo_id);
CREATE INDEX IF NOT EXISTS idx_fact_fin_entidad ON fact_financiero (entidad_id);

CREATE TABLE IF NOT EXISTS stg_ingest_log (
  ingest_id INTEGER PRIMARY KEY AUTOINCREMENT,
  rel_path TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  tamano_bytes INTEGER,
  entidad_codigo TEXT,
  registrado_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_stg_ingest_sha ON stg_ingest_log (sha256);
