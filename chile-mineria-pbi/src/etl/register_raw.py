from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

from sqlalchemy import text

from src.paths import default_db_path, get_engine, get_database_url, project_root


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    p = argparse.ArgumentParser(description="Registra archivos en data/raw (hash + manifest).")
    p.add_argument("--entity", help="Codigo entidad opcional (CODELCO, ESCONDIDA_BHP)", default=None)
    p.add_argument("--db", type=Path, default=None)
    p.add_argument("--database-url", default=None, help="URL SQLAlchemy para MySQL/otro motor")
    args = p.parse_args()

    root = project_root()
    raw = root / "data" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    manifest = root / "ingest_manifest.csv"
    db_path = args.db or default_db_path()

    rows: list[dict] = []
    for path in sorted(raw.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.suffix.lower() == ".md":
            continue
        digest = sha256_file(path)
        rel = path.relative_to(root).as_posix()
        rows.append(
            {
                "rel_path": rel,
                "sha256": digest,
                "tamano_bytes": path.stat().st_size,
                "entidad_codigo": args.entity or "",
            }
        )

    write_header = not manifest.exists()
    with manifest.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["rel_path", "sha256", "tamano_bytes", "entidad_codigo"],
        )
        if write_header:
            w.writeheader()
        for r in rows:
            w.writerow(r)

    db_url = get_database_url(db_path=db_path, database_url=args.database_url)
    should_write_db = True
    if db_url.startswith("sqlite+pysqlite:///") and not db_path.exists():
        should_write_db = False

    if should_write_db:
        eng = get_engine(db_path=db_path, database_url=args.database_url)
        insert_ignore = "INSERT IGNORE" if eng.dialect.name == "mysql" else "INSERT OR IGNORE"
        with eng.begin() as conn:
            for r in rows:
                conn.execute(
                    text(
                        f"{insert_ignore} INTO stg_ingest_log (rel_path, sha256, tamano_bytes, entidad_codigo) "
                        "VALUES (:rel_path, :sha256, :tamano_bytes, :entidad_codigo)"
                    ),
                    r,
                )

    print(f"Registrados {len(rows)} archivos en {manifest}")


if __name__ == "__main__":
    main()
