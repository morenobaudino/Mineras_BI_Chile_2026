from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_tabular_file(path: Path, sheet_name: str | int = 0) -> pd.DataFrame:
    suf = path.suffix.lower()
    if suf in (".xlsx", ".xlsm"):
        return pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
    if suf == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Formato no soportado: {path}")


def read_pdf_tables(path: Path, page_indices: list[int] | None = None) -> list[pd.DataFrame]:
    import pdfplumber

    out: list[pd.DataFrame] = []
    with pdfplumber.open(path) as pdf:
        idxs = page_indices if page_indices is not None else range(len(pdf.pages))
        for i in idxs:
            page = pdf.pages[int(i)]
            for table in page.extract_tables() or []:
                if not table or len(table) < 2:
                    continue
                header, *rows = table
                out.append(pd.DataFrame(rows, columns=header))
    return out
