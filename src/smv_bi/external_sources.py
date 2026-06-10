import json
import zipfile
from datetime import UTC, datetime
from html.parser import HTMLParser
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

from .config import (
    BRONZE_DIR,
    BVL_DAILY_SUMMARY_URL,
    GOLD_DIR,
    INEI_PBI_PERU_URL,
    MEF_BALANCE_EMPRESAS_ESTADO_RESOURCE_ID,
    MEF_DATASTORE_URL,
    SBS_OPEN_DATA,
    SILVER_DIR,
)


class SimpleTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._current_table: list[list[str]] | None = None
        self._current_row: list[str] | None = None
        self._current_cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "table":
            self._current_table = []
        elif tag == "tr" and self._current_table is not None:
            self._current_row = []
        elif tag in {"td", "th"} and self._current_row is not None:
            self._current_cell = []

    def handle_data(self, data: str) -> None:
        if self._current_cell is not None:
            value = " ".join(data.split())
            if value:
                self._current_cell.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._current_cell is not None and self._current_row is not None:
            self._current_row.append(" ".join(self._current_cell).strip())
            self._current_cell = None
        elif tag == "tr" and self._current_row is not None and self._current_table is not None:
            if any(cell for cell in self._current_row):
                self._current_table.append(self._current_row)
            self._current_row = None
        elif tag == "table" and self._current_table is not None:
            if self._current_table:
                self.tables.append(self._current_table)
            self._current_table = None


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def download_file(url: str, path: Path) -> dict:
    response = requests.get(
        url,
        timeout=90,
        headers={
            "User-Agent": "Mozilla/5.0 SMV360BI/1.0",
            "Referer": "https://www.sbs.gob.pe/estadisticas-y-publicaciones/estadisticas-/datos-abiertos_",
        },
    )
    response.raise_for_status()
    write_bytes(path, response.content)
    return {
        "url": url,
        "path": str(path),
        "status_code": response.status_code,
        "bytes": len(response.content),
        "content_type": response.headers.get("Content-Type", ""),
        "downloaded_at": datetime.now(UTC).isoformat(),
    }


def download_bvl() -> dict:
    response = requests.get(BVL_DAILY_SUMMARY_URL, timeout=60)
    response.raise_for_status()
    path = BRONZE_DIR / "bvl" / "boletin_diario" / "bolres.htm"
    write_text(path, response.text)
    return {
        "source": "BVL",
        "dataset": "Boletin diario - resumen",
        "url": BVL_DAILY_SUMMARY_URL,
        "path": str(path),
        "records": 1,
        "bytes": len(response.content),
        "status": "ok",
    }


def download_sbs() -> list[dict]:
    results = []
    for name, url in SBS_OPEN_DATA.items():
        zip_path = BRONZE_DIR / "sbs" / f"{name}.zip"
        meta = download_file(url, zip_path)
        extract_dir = BRONZE_DIR / "sbs" / name
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(extract_dir)
            members = [
                {
                    "dataset": name,
                    "member": info.filename,
                    "file_size": info.file_size,
                    "compress_size": info.compress_size,
                }
                for info in zf.infolist()
            ]
        inventory = pd.DataFrame(members)
        inventory.to_csv(
            SILVER_DIR / f"sbs_{name}_inventory.csv",
            index=False,
            encoding="utf-8-sig",
        )
        results.append(
            {
                "source": "SBS",
                "dataset": name,
                "url": url,
                "path": str(zip_path),
                "records": len(members),
                "bytes": meta["bytes"],
                "status": "ok",
            }
        )
    return results


def download_inei() -> dict:
    path = BRONZE_DIR / "inei" / "pbi" / "pbi_peru_16.xlsx"
    meta = download_file(INEI_PBI_PERU_URL, path)
    # The workbook has publication formatting. Silver keeps the raw rows for auditability.
    sheets = pd.read_excel(path, sheet_name=None, header=None)
    rows = []
    for sheet_name, sheet in sheets.items():
        sheet = sheet.dropna(how="all").dropna(axis=1, how="all")
        for idx, row in sheet.iterrows():
            rows.append(
                {
                    "sheet": sheet_name,
                    "row_number": int(idx) + 1,
                    "values": " | ".join("" if pd.isna(value) else str(value) for value in row.tolist()),
                }
            )
    pd.DataFrame(rows).to_csv(
        SILVER_DIR / "inei_pbi_peru_raw_rows.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return {
        "source": "INEI",
        "dataset": "PBI Peru por departamentos/actividades",
        "url": INEI_PBI_PERU_URL,
        "path": str(path),
        "records": len(rows),
        "bytes": meta["bytes"],
        "status": "ok",
    }


def download_mef() -> dict:
    params = {
        "resource_id": MEF_BALANCE_EMPRESAS_ESTADO_RESOURCE_ID,
        "limit": 5000,
    }
    response = requests.get(MEF_DATASTORE_URL, params=params, timeout=90)
    response.raise_for_status()
    payload = response.json()
    path = BRONZE_DIR / "mef" / "balance_empresas_estado_sample.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    records = payload.get("records", payload.get("result", {}).get("records", []))
    pd.DataFrame(records).to_csv(
        SILVER_DIR / "mef_balance_empresas_estado_sample.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return {
        "source": "MEF Datos Abiertos",
        "dataset": "Balance constructivo de empresas del Estado",
        "url": response.url,
        "path": str(path),
        "records": len(records),
        "bytes": len(response.content),
        "status": "ok",
    }


def build_bvl_silver() -> int:
    html_path = BRONZE_DIR / "bvl" / "boletin_diario" / "bolres.htm"
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    try:
        tables = pd.read_html(StringIO(html))
        parsed_tables = [
            table.dropna(how="all").dropna(axis=1, how="all").astype(str).values.tolist()
            for table in tables
        ]
    except (ValueError, ImportError):
        parser = SimpleTableParser()
        parser.feed(html)
        parsed_tables = parser.tables

    rows = []
    for table_index, table in enumerate(parsed_tables):
        for row_index, row in enumerate(table):
            rows.append(
                {
                    "table_index": table_index,
                    "row_index": int(row_index),
                    "values": " | ".join("" if pd.isna(value) else str(value) for value in row),
                }
            )
    pd.DataFrame(rows).to_csv(
        SILVER_DIR / "bvl_boletin_diario_tables.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return len(rows)


def run_external_sources() -> dict[str, int]:
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    coverage = []
    smv_files = list((BRONZE_DIR / "smv" / "principales_cuentas").glob("*.json"))
    smv_records = 0
    for path in smv_files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        smv_records += int(payload.get("d", {}).get("records", 0))
    coverage.append(
        {
            "source": "SMV",
            "dataset": "Principales cuentas financieras",
            "url": "https://mvnet.smv.gob.pe/ws_OD_EEFF/WebServiceInfoFinanciera.asmx/obtener_EFData",
            "path": str(BRONZE_DIR / "smv" / "principales_cuentas"),
            "records": smv_records,
            "bytes": sum(path.stat().st_size for path in smv_files),
            "status": "ok" if smv_files else "missing",
        }
    )

    bcrp_files = list((BRONZE_DIR / "bcrp" / "series").glob("*.json"))
    bcrp_records = 0
    for path in bcrp_files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        bcrp_records += len(payload.get("periods", []))
    coverage.append(
        {
            "source": "BCRP",
            "dataset": "Series macroeconomicas",
            "url": "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/",
            "path": str(BRONZE_DIR / "bcrp" / "series"),
            "records": bcrp_records,
            "bytes": sum(path.stat().st_size for path in bcrp_files),
            "status": "ok" if bcrp_files else "missing",
        }
    )

    bvl = download_bvl()
    bvl["records"] = build_bvl_silver()
    coverage.append(bvl)

    coverage.extend(download_sbs())
    coverage.append(download_inei())
    coverage.append(download_mef())

    coverage_df = pd.DataFrame(coverage)
    coverage_df.to_csv(GOLD_DIR / "source_coverage.csv", index=False, encoding="utf-8-sig")
    return {
        "sources_checked": coverage_df["source"].nunique(),
        "datasets_downloaded": len(coverage_df),
        "total_records_or_files": int(coverage_df["records"].fillna(0).sum()),
    }
