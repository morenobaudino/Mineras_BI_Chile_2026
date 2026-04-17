CREATE OR REPLACE VIEW vw_produccion_trimestral AS
SELECT
  t.anio,
  t.trimestre,
  t.periodo_inicio,
  t.periodo_fin,
  e.codigo AS entidad_codigo,
  e.nombre_mostrar AS entidad,
  e.holding,
  m.codigo AS metrica_codigo,
  m.nombre AS metrica_nombre,
  m.unidad AS metrica_unidad,
  p.valor,
  p.granularidad,
  p.source_file,
  p.extracted_at
FROM fact_produccion p
JOIN dim_tiempo t ON t.tiempo_id = p.tiempo_id
JOIN dim_entidad e ON e.entidad_id = p.entidad_id
JOIN dim_metrica m ON m.metrica_id = p.metrica_id
WHERE p.granularidad = 'quarter';

CREATE OR REPLACE VIEW vw_financiero_trimestral AS
SELECT
  t.anio,
  t.trimestre,
  t.periodo_inicio,
  t.periodo_fin,
  e.codigo AS entidad_codigo,
  e.nombre_mostrar AS entidad,
  m.codigo AS metrica_codigo,
  m.nombre AS metrica_nombre,
  m.unidad AS metrica_unidad,
  f.valor,
  f.moneda,
  f.fx_a_usd,
  f.granularidad,
  f.source_file,
  f.extracted_at
FROM fact_financiero f
JOIN dim_tiempo t ON t.tiempo_id = f.tiempo_id
JOIN dim_entidad e ON e.entidad_id = f.entidad_id
JOIN dim_metrica m ON m.metrica_id = f.metrica_id
WHERE f.granularidad = 'quarter';

CREATE OR REPLACE VIEW vw_glosario_metricas AS
SELECT
  codigo,
  nombre,
  unidad,
  definicion,
  categoria
FROM dim_metrica;
