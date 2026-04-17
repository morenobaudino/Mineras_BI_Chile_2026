from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from sqlalchemy import text

from src.etl.transform_metrics import quarter_period
from src.paths import default_db_path, get_engine, project_root


def _run_sql_file(conn, path: Path) -> None:
    script = path.read_text(encoding="utf-8")
    for stmt in [s.strip() for s in script.split(";") if s.strip()]:
        conn.execute(text(stmt))


def apply_schema(engine, root: Path) -> None:
    if engine.dialect.name == "mysql":
        schema = root / "sql" / "schema.mysql.sql"
        views = root / "sql" / "views.mysql.sql"
    else:
        schema = root / "sql" / "schema.sql"
        views = root / "sql" / "views.sql"
    with engine.begin() as conn:
        _run_sql_file(conn, schema)
        _run_sql_file(conn, views)


def seed_demo(engine, root: Path) -> None:
    cfg = yaml.safe_load((root / "src" / "config" / "entities.yaml").read_text(encoding="utf-8"))
    insert_ignore = "INSERT IGNORE" if engine.dialect.name == "mysql" else "INSERT OR IGNORE"
    with engine.begin() as conn:
        for e in cfg.get("entidades", []):
            conn.execute(
                text(
                    f"{insert_ignore} INTO dim_entidad (codigo, nombre_mostrar, holding, tipo, pais, es_jv, pct_participacion, notas) "
                    "VALUES (:codigo, :nombre_mostrar, :holding, :tipo, :pais, :es_jv, :pct_participacion, :notas)"
                ),
                {
                    "codigo": e["codigo"],
                    "nombre_mostrar": e["nombre_mostrar"],
                    "holding": e.get("holding"),
                    "tipo": e.get("tipo"),
                    "pais": e.get("pais", "CL"),
                    "es_jv": 1 if e.get("es_jv") else 0,
                    "pct_participacion": e.get("pct_participacion"),
                    "notas": e.get("notas"),
                },
            )

        metrics = [
            (
                "cu_production_kt",
                "Producción cobre fino",
                "kt",
                "Miles de toneladas métricas de cobre fino (ajustar definición a la fuente).",
                "produccion",
            ),
            (
                "c1_cost_usd_lb",
                "Costo C1 (referencial)",
                "USD/lb",
                "Costo neto de efectivo antes de by-product credits; definición depende del emisor.",
                "costo",
            ),
            (
                "ebitda_usd_m",
                "EBITDA",
                "USD millones",
                "Resultado operacional aproximado; ver notas del reporte.",
                "finanzas",
            ),
            (
                "net_income_usd_m",
                "Utilidad neta atribuible",
                "USD millones",
                "Utilidad neta según reporte (puede ser segmento o grupo).",
                "finanzas",
            ),
        ]
        for codigo, nombre, unidad, definicion, categoria in metrics:
            conn.execute(
                text(
                    f"{insert_ignore} INTO dim_metrica (codigo, nombre, unidad, definicion, categoria) "
                    "VALUES (:codigo, :nombre, :unidad, :definicion, :categoria)"
                ),
                {
                    "codigo": codigo,
                    "nombre": nombre,
                    "unidad": unidad,
                    "definicion": definicion,
                    "categoria": categoria,
                },
            )

        periods = [(2024, 1), (2024, 2)]
        for year, q in periods:
            start, end = quarter_period(year, q)
            conn.execute(
                text(
                    f"{insert_ignore} INTO dim_tiempo (periodo_inicio, periodo_fin, anio, trimestre, mes, granularidad) "
                    "VALUES (:ini, :fin, :anio, :trimestre, NULL, 'quarter')"
                ),
                {"ini": start.isoformat(), "fin": end.isoformat(), "anio": year, "trimestre": q},
            )

        def ids() -> dict:
            ent = {r[0]: r[1] for r in conn.execute(text("SELECT codigo, entidad_id FROM dim_entidad")).all()}
            met = {r[0]: r[1] for r in conn.execute(text("SELECT codigo, metrica_id FROM dim_metrica")).all()}
            tim = {
                (r[0], r[1]): r[2]
                for r in conn.execute(text("SELECT anio, trimestre, tiempo_id FROM dim_tiempo")).all()
            }
            return ent, met, tim

        ent, met, tim = ids()

        conn.execute(text("DELETE FROM fact_produccion WHERE source_file = 'SEED_DEMO'"))
        conn.execute(text("DELETE FROM fact_financiero WHERE source_file = 'SEED_DEMO'"))

        demo_prod = [
            ("CODELCO", 2024, 1, "cu_production_kt", 395.0),
            ("CODELCO", 2024, 2, "cu_production_kt", 402.0),
            ("ESCONDIDA_BHP", 2024, 1, "cu_production_kt", 280.0),
            ("ESCONDIDA_BHP", 2024, 2, "cu_production_kt", 275.0),
        ]
        for cod_ent, year, q, mcode, val in demo_prod:
            conn.execute(
                text(
                    "INSERT INTO fact_produccion (tiempo_id, entidad_id, metrica_id, valor, granularidad, source_file, notes) "
                    "VALUES (:tid, :eid, :mid, :val, 'quarter', 'SEED_DEMO', 'Datos ilustrativos para cablear Power BI; reemplazar con extracción real.')"
                ),
                {
                    "tid": tim[(year, q)],
                    "eid": ent[cod_ent],
                    "mid": met[mcode],
                    "val": val,
                },
            )

        demo_fin = [
            ("CODELCO", 2024, 1, "ebitda_usd_m", 2100.0),
            ("CODELCO", 2024, 2, "ebitda_usd_m", 2250.0),
            ("CODELCO", 2024, 1, "net_income_usd_m", 450.0),
            ("ESCONDIDA_BHP", 2024, 1, "ebitda_usd_m", 3200.0),
            ("ESCONDIDA_BHP", 2024, 2, "ebitda_usd_m", 3050.0),
        ]
        for cod_ent, year, q, mcode, val in demo_fin:
            conn.execute(
                text(
                    "INSERT INTO fact_financiero (tiempo_id, entidad_id, metrica_id, valor, moneda, granularidad, source_file, notes) "
                    "VALUES (:tid, :eid, :mid, :val, 'USD', 'quarter', 'SEED_DEMO', 'Datos ilustrativos; BHP suele reportar USD consolidado — revisar atribución a Escondida.')"
                ),
                {
                    "tid": tim[(year, q)],
                    "eid": ent[cod_ent],
                    "mid": met[mcode],
                    "val": val,
                },
            )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=None)
    ap.add_argument("--database-url", default=None, help="Ejemplo: mysql+pymysql://user:pass@localhost:3306/chile_mineria_pbi")
    ap.add_argument("--schema-only", action="store_true")
    ap.add_argument("--seed", action="store_true", help="Inserta entidades + demo 2024Q1/Q2")
    args = ap.parse_args()

    root = project_root()
    db_path = args.db or default_db_path()
    if not args.database_url:
        db_path.parent.mkdir(parents=True, exist_ok=True)

    eng = get_engine(db_path=db_path, database_url=args.database_url)
    apply_schema(eng, root)
    if args.seed:
        seed_demo(eng, root)
    print(f"Listo en motor: {eng.dialect.name}")


if __name__ == "__main__":
    main()
