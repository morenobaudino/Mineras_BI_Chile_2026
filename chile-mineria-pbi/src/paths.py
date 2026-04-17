from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine  


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_db_path() -> Path:
    return project_root() / "data" / "mineria_chile.db"


def get_database_url(db_path: Path | None = None, database_url: str | None = None) -> str:
    # 1. Prioridad: URL directa (si existe)
    if database_url:
        return database_url
    
    # 2. Configuración para tu MySQL Workbench
    usuario = "root"
    password = "More2323" # <--- COLOCA TU CLAVE DE MYSQL
    host = "localhost"
    db_name = "chile_mineria_pbi"
    
    return f"mysql+pymysql://{usuario}:{password}@{host}:3306/{db_name}"


def get_engine(
    db_path: Path | None = None,
    database_url: str | None = None,
):
    url = get_database_url(db_path=db_path, database_url=database_url)
    return create_engine(url, pool_pre_ping=True)
    
