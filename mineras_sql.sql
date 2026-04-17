SELECT 
    e.nombre_mostrar AS Minera,
    SUM(CASE WHEN m.codigo = 'cu_production_kt' THEN f.valor ELSE 0 END) AS Total_Produccion_KT,
    SUM(CASE WHEN m.codigo = 'ebitda_usd_m' THEN f.valor ELSE 0 END) AS Total_EBITDA_USD_M
FROM fact_produccion f
JOIN dim_entidad e ON f.entidad_id = e.entidad_id
JOIN dim_metrica m ON f.metrica_id = m.metrica_id
GROUP BY e.nombre_mostrar
ORDER BY Total_Produccion_KT DESC;
USE chile_mineria_pbi;