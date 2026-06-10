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


MONTH_ES = {
    "Ene": 1,
    "Feb": 2,
    "Mar": 3,
    "Abr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Ago": 8,
    "Set": 9,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dic": 12,
}


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


def parse_sbs_period(value: str) -> pd.Timestamp:
    try:
        month_text, year_text = str(value).split("-")
        month = MONTH_ES.get(month_text.strip(), 1)
        year = int(year_text)
        return pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0)
    except Exception:
        return pd.NaT


def to_numeric_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def build_sbs_silver() -> int:
    esf_path = (
        BRONZE_DIR
        / "sbs"
        / "sistema_financiero_estado_situacion"
        / "ESF_SF"
        / "dataset_sf_esf.csv"
    )
    er_path = (
        BRONZE_DIR
        / "sbs"
        / "sistema_financiero_estado_resultados"
        / "ER_SF"
        / "dataset_sf_er.csv"
    )
    esf = pd.read_csv(esf_path)
    er = pd.read_csv(er_path)

    esf_cols = [
        "PERIODO",
        "ENTIDAD",
        "TOTAL_ACTIVO",
        "TOTAL_PASIVO",
        "PATRIMONIO",
        "CREDITOS",
        "ATRASADOS",
        "VENCIDOS",
        "EN_COBRANZA_JUDICIAL",
    ]
    er_cols = [
        "PERIODO",
        "ENTIDAD",
        "MARGEN_FINANCIERO_BRUTO",
        "MARGEN_FINANCIERO_NETO",
        "RESULTADO_NETO_DEL_EJERCICIO",
    ]
    esf = esf[[column for column in esf_cols if column in esf.columns]].copy()
    er = er[[column for column in er_cols if column in er.columns]].copy()
    esf = to_numeric_columns(esf, [column for column in esf.columns if column not in {"PERIODO", "ENTIDAD"}])
    er = to_numeric_columns(er, [column for column in er.columns if column not in {"PERIODO", "ENTIDAD"}])

    sbs = esf.merge(er, on=["PERIODO", "ENTIDAD"], how="outer")
    sbs["fecha"] = sbs["PERIODO"].map(parse_sbs_period)
    sbs["anio"] = sbs["fecha"].dt.year
    sbs["mes"] = sbs["fecha"].dt.month
    sbs["ratio_atrasados"] = sbs["ATRASADOS"] / sbs["CREDITOS"].replace({0: pd.NA})
    sbs["roa_sbs"] = sbs["RESULTADO_NETO_DEL_EJERCICIO"] / sbs["TOTAL_ACTIVO"].replace({0: pd.NA})
    sbs["roe_sbs"] = sbs["RESULTADO_NETO_DEL_EJERCICIO"] / sbs["PATRIMONIO"].replace({0: pd.NA})
    sbs.columns = [column.lower() for column in sbs.columns]
    sbs.to_csv(SILVER_DIR / "sbs_financial_system_kpis.csv", index=False, encoding="utf-8-sig")
    return len(sbs)


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


def clean_year(value) -> int | None:
    text = str(value).replace("P/", "").replace("E/", "").replace(".0", "").strip()
    try:
        return int(float(text))
    except ValueError:
        return None


def extract_inei_table(path: Path, sheet_name: str, value_name: str) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None)
    header = raw.iloc[6].tolist()
    years = [clean_year(value) for value in header[1:]]
    records = []
    for _, row in raw.iloc[8:].iterrows():
        department = row.iloc[0]
        if pd.isna(department):
            continue
        department_text = str(department).strip()
        if not department_text or department_text.lower().startswith("nota"):
            continue
        for position, year in enumerate(years, start=1):
            if year is None:
                continue
            value = pd.to_numeric(row.iloc[position], errors="coerce")
            if pd.isna(value):
                continue
            records.append(
                {
                    "departamento": department_text,
                    "anio": year,
                    value_name: value,
                }
            )
    return pd.DataFrame(records)


def build_inei_silver() -> int:
    path = BRONZE_DIR / "inei" / "pbi" / "pbi_peru_16.xlsx"
    pbi = extract_inei_table(path, "Cuadro1", "pbi_miles_soles_2007")
    share = extract_inei_table(path, "Cuadro2", "participacion_pbi")
    growth = extract_inei_table(path, "Cuadro3", "variacion_pbi")
    result = pbi.merge(share, on=["departamento", "anio"], how="left").merge(
        growth, on=["departamento", "anio"], how="left"
    )
    result.to_csv(SILVER_DIR / "inei_pbi_departamental.csv", index=False, encoding="utf-8-sig")
    return len(result)


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


def build_mef_silver() -> int:
    path = SILVER_DIR / "mef_balance_empresas_estado_sample.csv"
    mef = pd.read_csv(path)
    amount_cols = [column for column in mef.columns if column.startswith("MONTO")]
    mef = to_numeric_columns(mef, amount_cols)
    for column in ["ANO_EJE", "MES_EJE"]:
        if column in mef.columns:
            mef[column] = pd.to_numeric(mef[column], errors="coerce")
    group_cols = [
        "ANO_EJE",
        "MES_EJE",
        "DEPARTAMENTO_EJECUTORA_NOMBRE",
        "PROVINCIA_EJECUTORA_NOMBRE",
        "ENTIDAD",
        "ENTIDAD_NOMBRE",
        "NIVEL_NOMBRE",
        "RUBRO_NOMBRE",
    ]
    group_cols = [column for column in group_cols if column in mef.columns]
    amount = "MONTO4" if "MONTO4" in mef.columns else amount_cols[0]
    result = (
        mef.groupby(group_cols, dropna=False)
        .agg(monto_total=(amount, "sum"), registros=(amount, "size"))
        .reset_index()
    )
    result.columns = [column.lower() for column in result.columns]
    result.to_csv(SILVER_DIR / "mef_empresas_estado_resumen.csv", index=False, encoding="utf-8-sig")
    return len(result)


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
    build_bvl_market_snapshot(rows)
    return len(rows)


def parse_decimal(text: str) -> float | None:
    cleaned = (
        str(text)
        .replace("US$", "")
        .replace("S/", "")
        .replace("%", "")
        .replace(",", "")
        .strip()
    )
    try:
        return float(cleaned)
    except ValueError:
        return None


def build_bvl_market_snapshot(rows: list[dict]) -> int:
    records = []
    values = [row["values"] for row in rows]
    for value in values:
        parts = [part.strip() for part in value.split("|")]
        if len(parts) >= 5 and parts[0].startswith("MSCI"):
            records.append(
                {
                    "categoria": "indice",
                    "nombre": parts[0],
                    "valor_1": parse_decimal(parts[1]),
                    "valor_2": parse_decimal(parts[2]),
                    "valor_3": parse_decimal(parts[3]),
                    "valor_4": parse_decimal(parts[4]),
                    "raw": value,
                }
            )
        elif value.startswith("Subieron:"):
            records.append(
                {
                    "categoria": "amplitud_mercado",
                    "nombre": "subieron_bajaron_mantuvieron",
                    "valor_1": parse_decimal(parts[1]) if len(parts) > 1 else None,
                    "valor_2": parse_decimal(parts[3]) if len(parts) > 3 else None,
                    "valor_3": parse_decimal(parts[5]) if len(parts) > 5 else None,
                    "valor_4": None,
                    "raw": value,
                }
            )
        elif len(parts) == 2 and "Capitalizaci" not in value:
            first = parse_decimal(parts[0])
            second = parse_decimal(parts[1])
            if first is not None and second is not None:
                records.append(
                    {
                        "categoria": "capitalizacion",
                        "nombre": "capitalizacion_total",
                        "valor_1": first,
                        "valor_2": second,
                        "valor_3": None,
                        "valor_4": None,
                        "raw": value,
                    }
                )
    snapshot = pd.DataFrame(records)
    snapshot.to_csv(SILVER_DIR / "bvl_market_snapshot.csv", index=False, encoding="utf-8-sig")
    return len(snapshot)


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
    build_sbs_silver()
    coverage.append(download_inei())
    build_inei_silver()
    coverage.append(download_mef())
    build_mef_silver()

    coverage_df = pd.DataFrame(coverage)
    coverage_df.to_csv(GOLD_DIR / "source_coverage.csv", index=False, encoding="utf-8-sig")
    return {
        "sources_checked": coverage_df["source"].nunique(),
        "datasets_downloaded": len(coverage_df),
        "total_records_or_files": int(coverage_df["records"].fillna(0).sum()),
    }
