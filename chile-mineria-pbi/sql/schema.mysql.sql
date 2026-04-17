CREATE TABLE IF NOT EXISTS dim_tiempo (
  tiempo_id INT AUTO_INCREMENT PRIMARY KEY,
  periodo_inicio DATE NOT NULL,
  periodo_fin DATE NOT NULL,
  anio INT NOT NULL,
  trimestre INT,
  mes INT,
  granularidad VARCHAR(16) NOT NULL,
  UNIQUE KEY uq_tiempo_periodo (periodo_inicio, periodo_fin, granularidad),
  CONSTRAINT chk_dim_tiempo_gran CHECK (granularidad IN ('day', 'month', 'quarter', 'year'))
);

CREATE TABLE IF NOT EXISTS dim_entidad (
  entidad_id INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(64) NOT NULL UNIQUE,
  nombre_mostrar VARCHAR(255) NOT NULL,
  holding VARCHAR(255),
  tipo VARCHAR(64),
  pais VARCHAR(8) NOT NULL DEFAULT 'CL',
  es_jv TINYINT(1) NOT NULL DEFAULT 0,
  pct_participacion DECIMAL(6,3),
  notas TEXT,
  CONSTRAINT chk_dim_entidad_es_jv CHECK (es_jv IN (0, 1))
);

CREATE TABLE IF NOT EXISTS dim_metrica (
  metrica_id INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(64) NOT NULL UNIQUE,
  nombre VARCHAR(255) NOT NULL,
  unidad VARCHAR(64),
  definicion TEXT,
  categoria VARCHAR(32) NOT NULL,
  CONSTRAINT chk_dim_metrica_categoria CHECK (categoria IN ('produccion', 'finanzas', 'costo', 'otro'))
);

CREATE TABLE IF NOT EXISTS fact_produccion (
  fact_prod_id INT AUTO_INCREMENT PRIMARY KEY,
  tiempo_id INT NOT NULL,
  entidad_id INT NOT NULL,
  metrica_id INT NOT NULL,
  valor DECIMAL(18,4) NOT NULL,
  granularidad VARCHAR(16) NOT NULL,
  source_file VARCHAR(512),
  source_page VARCHAR(64),
  extracted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  notes TEXT,
  KEY idx_fact_prod_tiempo (tiempo_id),
  KEY idx_fact_prod_entidad (entidad_id),
  CONSTRAINT fk_fact_prod_tiempo FOREIGN KEY (tiempo_id) REFERENCES dim_tiempo (tiempo_id),
  CONSTRAINT fk_fact_prod_entidad FOREIGN KEY (entidad_id) REFERENCES dim_entidad (entidad_id),
  CONSTRAINT fk_fact_prod_metrica FOREIGN KEY (metrica_id) REFERENCES dim_metrica (metrica_id)
);

CREATE TABLE IF NOT EXISTS fact_financiero (
  fact_fin_id INT AUTO_INCREMENT PRIMARY KEY,
  tiempo_id INT NOT NULL,
  entidad_id INT NOT NULL,
  metrica_id INT NOT NULL,
  valor DECIMAL(18,4) NOT NULL,
  moneda VARCHAR(8) NOT NULL DEFAULT 'USD',
  fx_a_usd DECIMAL(18,8),
  granularidad VARCHAR(16) NOT NULL,
  source_file VARCHAR(512),
  source_page VARCHAR(64),
  extracted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  notes TEXT,
  KEY idx_fact_fin_tiempo (tiempo_id),
  KEY idx_fact_fin_entidad (entidad_id),
  CONSTRAINT fk_fact_fin_tiempo FOREIGN KEY (tiempo_id) REFERENCES dim_tiempo (tiempo_id),
  CONSTRAINT fk_fact_fin_entidad FOREIGN KEY (entidad_id) REFERENCES dim_entidad (entidad_id),
  CONSTRAINT fk_fact_fin_metrica FOREIGN KEY (metrica_id) REFERENCES dim_metrica (metrica_id)
);

CREATE TABLE IF NOT EXISTS stg_ingest_log (
  ingest_id INT AUTO_INCREMENT PRIMARY KEY,
  rel_path VARCHAR(1024) NOT NULL,
  sha256 CHAR(64) NOT NULL,
  tamano_bytes BIGINT,
  entidad_codigo VARCHAR(64),
  registrado_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_ingest_sha (sha256)
);
