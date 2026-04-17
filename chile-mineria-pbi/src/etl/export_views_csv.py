from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.paths import default_db_path, get_engine, project_root


def main() -> None:
    p = argparse.ArgumentParser(description="Exporta vistas SQL a CSV para Power BI.")
    p.add_argument("--db", type=Path, default=None)
    p.add_argument("--database-url", default=None, help="URL SQLAlchemy para MySQL/otro motor")
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Carpeta de salida (default: data/processed/pbi_export)",
    )
    args = p.parse_args()
    db_path = args.db or default_db_path()
    out_dir = args.out or (project_root() / "data" / "processed" / "pbi_export")
    out_dir.mkdir(parents=True, exist_ok=True)

    eng = get_engine(db_path=db_path, database_url=args.database_url)
    views = [
        "vw_produccion_trimestral",
        "vw_financiero_trimestral",
        "vw_glosario_metricas",
    ]
    for v in views:
        df = pd.read_sql(f"SELECT * FROM {v}", eng)
        dest = out_dir / f"{v}.csv"
        df.to_csv(dest, index=False, encoding="utf-8-sig")
        print(dest)


if __name__ == "__main__":
    main()
