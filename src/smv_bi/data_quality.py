from pathlib import Path

import pandas as pd

from .config import GOLD_DIR, SILVER_DIR


PROFILE_TARGETS = {
    "silver_smv_principales_cuentas": SILVER_DIR / "smv_principales_cuentas.csv",
    "silver_bcrp_series": SILVER_DIR / "bcrp_series_long.csv",
    "silver_sbs_financial_system": SILVER_DIR / "sbs_financial_system_kpis.csv",
    "silver_inei_pbi_departamental": SILVER_DIR / "inei_pbi_departamental.csv",
    "silver_mef_empresas_estado": SILVER_DIR / "mef_empresas_estado_resumen.csv",
    "silver_bvl_market_snapshot": SILVER_DIR / "bvl_market_snapshot.csv",
    "gold_financial_kpis": GOLD_DIR / "fact_financial_kpis.csv",
    "gold_sbs_financial_system": GOLD_DIR / "fact_sbs_financial_system.csv",
    "gold_inei_pbi_department": GOLD_DIR / "fact_inei_pbi_department.csv",
    "gold_mef_state_enterprises": GOLD_DIR / "fact_mef_state_enterprises.csv",
    "gold_bvl_market_snapshot": GOLD_DIR / "fact_bvl_market_snapshot.csv",
}


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def profile_table(name: str, path: Path, df: pd.DataFrame) -> dict:
    return {
        "table_name": name,
        "path": str(path),
        "rows": len(df),
        "columns": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_cells": int(df.isna().sum().sum()),
        "missing_pct": round(float(df.isna().sum().sum() / max(len(df) * len(df.columns), 1)), 6),
        "numeric_columns": int(len(df.select_dtypes(include="number").columns)),
        "text_columns": int(len(df.select_dtypes(include="object").columns)),
    }


def profile_columns(name: str, df: pd.DataFrame) -> list[dict]:
    rows = []
    for column in df.columns:
        series = df[column]
        numeric = pd.to_numeric(series, errors="coerce")
        is_numeric = numeric.notna().sum() > 0 and series.dtype != "object" or numeric.notna().sum() >= len(series) * 0.8
        rows.append(
            {
                "table_name": name,
                "column_name": column,
                "dtype": str(series.dtype),
                "non_null": int(series.notna().sum()),
                "nulls": int(series.isna().sum()),
                "null_pct": round(float(series.isna().mean()), 6),
                "distinct_values": int(series.nunique(dropna=True)),
                "min_value": numeric.min() if is_numeric else None,
                "max_value": numeric.max() if is_numeric else None,
                "mean_value": numeric.mean() if is_numeric else None,
            }
        )
    return rows


def add_check(checks: list[dict], table: str, check_name: str, passed: bool, detail: str) -> None:
    checks.append(
        {
            "table_name": table,
            "check_name": check_name,
            "status": "pass" if passed else "fail",
            "detail": detail,
        }
    )


def build_quality_checks(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    checks: list[dict] = []

    smv = frames.get("gold_financial_kpis")
    if smv is not None:
        add_check(checks, "gold_financial_kpis", "has_rows", len(smv) > 0, f"rows={len(smv)}")
        add_check(checks, "gold_financial_kpis", "company_key_not_null", smv["rpj"].notna().all(), "rpj not null")
        add_check(checks, "gold_financial_kpis", "assets_positive", (smv["activo_total"] > 0).all(), "activo_total > 0")
        add_check(
            checks,
            "gold_financial_kpis",
            "risk_score_range",
            smv["score_riesgo"].between(0, 100).all(),
            "score_riesgo between 0 and 100",
        )

    sbs = frames.get("gold_sbs_financial_system")
    if sbs is not None:
        add_check(checks, "gold_sbs_financial_system", "has_rows", len(sbs) > 0, f"rows={len(sbs)}")
        add_check(checks, "gold_sbs_financial_system", "entity_not_null", sbs["entidad"].notna().all(), "entidad not null")
        add_check(
            checks,
            "gold_sbs_financial_system",
            "assets_non_negative",
            (sbs["total_activo"].fillna(0) >= 0).all(),
            "total_activo >= 0",
        )

    inei = frames.get("gold_inei_pbi_department")
    if inei is not None:
        add_check(checks, "gold_inei_pbi_department", "has_rows", len(inei) > 0, f"rows={len(inei)}")
        add_check(checks, "gold_inei_pbi_department", "year_range", inei["anio"].between(2007, 2026).all(), "anio in expected range")
        add_check(
            checks,
            "gold_inei_pbi_department",
            "pbi_non_negative",
            (inei["pbi_miles_soles_2007"].fillna(0) >= 0).all(),
            "pbi >= 0",
        )

    coverage = GOLD_DIR / "source_coverage.csv"
    if coverage.exists():
        source_coverage = read_csv(coverage)
        add_check(
            checks,
            "source_coverage",
            "six_sources_present",
            source_coverage["source"].nunique() >= 6,
            f"sources={source_coverage['source'].nunique()}",
        )
        add_check(
            checks,
            "source_coverage",
            "all_sources_ok",
            (source_coverage["status"] == "ok").all(),
            "all source status values are ok",
        )

    return pd.DataFrame(checks)


def run_data_quality() -> dict[str, int]:
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    table_profiles = []
    column_profiles = []
    frames: dict[str, pd.DataFrame] = {}

    for name, path in PROFILE_TARGETS.items():
        if not path.exists():
            continue
        df = read_csv(path)
        frames[name] = df
        table_profiles.append(profile_table(name, path, df))
        column_profiles.extend(profile_columns(name, df))

    tables = pd.DataFrame(table_profiles)
    columns = pd.DataFrame(column_profiles)
    checks = build_quality_checks(frames)

    tables.to_csv(GOLD_DIR / "data_profile_tables.csv", index=False, encoding="utf-8-sig")
    columns.to_csv(GOLD_DIR / "data_profile_columns.csv", index=False, encoding="utf-8-sig")
    checks.to_csv(GOLD_DIR / "data_quality_results.csv", index=False, encoding="utf-8-sig")

    return {
        "profiled_tables": len(tables),
        "profiled_columns": len(columns),
        "quality_checks": len(checks),
        "quality_failures": int((checks["status"] == "fail").sum()) if not checks.empty else 0,
    }
