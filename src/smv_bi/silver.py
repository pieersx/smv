import json
import re
from pathlib import Path

import pandas as pd

from .config import BRONZE_DIR, SILVER_DIR


PERIOD_MAP = {
    "1": "Q1",
    "2": "Q2",
    "3": "Q3",
    "4": "Q4",
    "A": "FY",
    "Anual": "FY",
    "1er Trimestre": "Q1",
    "2do Trimestre": "Q2",
    "3er Trimestre": "Q3",
    "4to Trimestre": "Q4",
}


def period_sort(period: str) -> int:
    return {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4, "FY": 5}.get(period, 0)


def parse_number(value) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = str(value).replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def normalize_text(value) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def build_smv_silver() -> pd.DataFrame:
    rows: list[dict] = []
    for path in sorted((BRONZE_DIR / "smv" / "principales_cuentas").glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        metadata = payload.get("_metadata", {})
        for row in payload.get("d", {}).get("rows", []):
            period_raw = normalize_text(row.get("Trimestre"))
            period = PERIOD_MAP.get(period_raw, period_raw)
            if period not in {"Q1", "Q2", "Q3", "Q4", "FY"}:
                period = PERIOD_MAP.get(str(metadata.get("params", {}).get("periodo")), period)

            rows.append(
                {
                    "rpj": normalize_text(row.get("RPJ")),
                    "tipo_empresa": normalize_text(row.get("TipoEmpresa")),
                    "tipo_sector": normalize_text(row.get("TipoSector")),
                    "nombre_empresa": normalize_text(row.get("NombreEmpresa")),
                    "ruc": normalize_text(row.get("RUC")),
                    "ciiu": normalize_text(row.get("CIIU")),
                    "ejercicio": int(row.get("Ejercicio")),
                    "periodo": period,
                    "periodo_orden": period_sort(period),
                    "tipo_informacion": normalize_text(row.get("TipoInformacion")),
                    "moneda": normalize_text(row.get("Moneda")),
                    "metodo_flujo_efectivo": normalize_text(row.get("MetodoFlujoEfectivo")),
                    "activo_total": parse_number(row.get("ActivoTotal")),
                    "patrimonio_total": parse_number(row.get("PatrimonioTotal")),
                    "total_ingreso": parse_number(row.get("TotalIngreso")),
                    "utilidad_neta": parse_number(row.get("UtilidadNeta")),
                    "pasivo_total": parse_number(row.get("PasivoTotal")),
                    "source_file": str(path.relative_to(BRONZE_DIR.parents[0])),
                }
            )

    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("No SMV bronze files found. Run bronze first.")

    df = df.drop_duplicates(
        subset=["rpj", "ruc", "ejercicio", "periodo", "tipo_informacion"],
        keep="last",
    )
    df = df.sort_values(["ejercicio", "periodo_orden", "nombre_empresa"]).reset_index(drop=True)

    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(SILVER_DIR / "smv_principales_cuentas.csv", index=False, encoding="utf-8-sig")
    return df


def parse_bcrp_date(value: str) -> pd.Timestamp:
    month_map = {
        "Ene": "Jan",
        "Feb": "Feb",
        "Mar": "Mar",
        "Abr": "Apr",
        "May": "May",
        "Jun": "Jun",
        "Jul": "Jul",
        "Ago": "Aug",
        "Set": "Sep",
        "Sep": "Sep",
        "Oct": "Oct",
        "Nov": "Nov",
        "Dic": "Dec",
    }
    normalized = value
    for es, en in month_map.items():
        normalized = normalized.replace(es, en)
    return pd.to_datetime(normalized, dayfirst=True, errors="coerce")


def build_bcrp_silver() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for path in sorted((BRONZE_DIR / "bcrp" / "series").glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        meta = payload.get("_metadata", {})
        series_name = meta.get("series_name", path.stem)
        records = []
        for period in payload.get("periods", []):
            values = period.get("values") or [None]
            records.append(
                {
                    "fecha": parse_bcrp_date(period.get("name", "")),
                    "serie": series_name,
                    "valor": parse_number(values[0]),
                }
            )
        frames.append(pd.DataFrame(records))

    if not frames:
        raise RuntimeError("No BCRP bronze files found. Run bronze first.")

    df = pd.concat(frames, ignore_index=True)
    df = df.dropna(subset=["fecha"]).sort_values(["fecha", "serie"])
    wide = df.pivot_table(index="fecha", columns="serie", values="valor", aggfunc="last").reset_index()
    wide.columns.name = None
    wide["anio"] = wide["fecha"].dt.year
    wide["mes"] = wide["fecha"].dt.month

    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(SILVER_DIR / "bcrp_series_long.csv", index=False, encoding="utf-8-sig")
    wide.to_csv(SILVER_DIR / "bcrp_series_wide.csv", index=False, encoding="utf-8-sig")
    return wide


def run_silver() -> dict[str, int]:
    smv = build_smv_silver()
    bcrp = build_bcrp_silver()
    return {
        "smv_rows": len(smv),
        "bcrp_rows": len(bcrp),
    }
