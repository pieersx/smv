import pandas as pd

from .config import GOLD_DIR, SILVER_DIR


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    result = numerator / denominator.replace({0: pd.NA})
    return pd.to_numeric(result, errors="coerce")


def risk_bucket(score: float) -> str:
    if pd.isna(score):
        return "Sin datos"
    if score >= 70:
        return "Alto"
    if score >= 40:
        return "Medio"
    return "Bajo"


def build_gold() -> dict[str, pd.DataFrame]:
    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    smv = pd.read_csv(SILVER_DIR / "smv_principales_cuentas.csv")
    smv = smv[
        (smv["moneda"].str.upper() == "SOLES")
        & smv["activo_total"].notna()
        & (smv["activo_total"] > 0)
    ].copy()

    smv["roa"] = safe_divide(smv["utilidad_neta"], smv["activo_total"])
    smv["roe"] = safe_divide(smv["utilidad_neta"], smv["patrimonio_total"])
    smv["endeudamiento"] = safe_divide(smv["pasivo_total"], smv["activo_total"])
    smv["apalancamiento"] = safe_divide(smv["pasivo_total"], smv["patrimonio_total"])
    smv["margen_neto"] = safe_divide(smv["utilidad_neta"], smv["total_ingreso"])

    smv = smv.sort_values(["rpj", "periodo_orden", "ejercicio"])
    smv["crecimiento_ingresos"] = smv.groupby(["rpj", "periodo"])["total_ingreso"].pct_change()
    smv["crecimiento_utilidad"] = smv.groupby(["rpj", "periodo"])["utilidad_neta"].pct_change()

    # Score pragmatico para BI academico: mayor deuda, perdidas y deterioro suben el riesgo.
    smv["riesgo_endeudamiento"] = (smv["endeudamiento"].clip(lower=0, upper=1.5) / 1.5) * 35
    smv["riesgo_roa"] = ((0.08 - smv["roa"]).clip(lower=0, upper=0.20) / 0.20) * 25
    smv["riesgo_margen"] = ((0.10 - smv["margen_neto"]).clip(lower=0, upper=0.30) / 0.30) * 20
    smv["riesgo_crecimiento"] = ((-smv["crecimiento_utilidad"]).clip(lower=0, upper=1.0)) * 20
    smv["score_riesgo"] = (
        smv[
            [
                "riesgo_endeudamiento",
                "riesgo_roa",
                "riesgo_margen",
                "riesgo_crecimiento",
            ]
        ]
        .fillna(0)
        .sum(axis=1)
        .clip(0, 100)
        .round(2)
    )
    smv["nivel_riesgo"] = smv["score_riesgo"].map(risk_bucket)
    smv["periodo_label"] = smv["ejercicio"].astype(str) + "-" + smv["periodo"]

    dim_empresa = (
        smv.sort_values(["ejercicio", "periodo_orden"])
        .drop_duplicates(subset=["rpj"], keep="last")
        [
            [
                "rpj",
                "ruc",
                "nombre_empresa",
                "tipo_empresa",
                "tipo_sector",
                "ciiu",
            ]
        ]
        .sort_values("nombre_empresa")
        .reset_index(drop=True)
    )

    fact_financial_kpis = smv[
        [
            "rpj",
            "ruc",
            "nombre_empresa",
            "tipo_empresa",
            "tipo_sector",
            "ejercicio",
            "periodo",
            "periodo_orden",
            "periodo_label",
            "activo_total",
            "pasivo_total",
            "patrimonio_total",
            "total_ingreso",
            "utilidad_neta",
            "roa",
            "roe",
            "endeudamiento",
            "apalancamiento",
            "margen_neto",
            "crecimiento_ingresos",
            "crecimiento_utilidad",
            "score_riesgo",
            "nivel_riesgo",
        ]
    ].copy()

    fact_sector_risk = (
        fact_financial_kpis.groupby(["ejercicio", "periodo", "periodo_orden", "tipo_sector"], dropna=False)
        .agg(
            empresas=("rpj", "nunique"),
            activo_total=("activo_total", "sum"),
            pasivo_total=("pasivo_total", "sum"),
            utilidad_neta=("utilidad_neta", "sum"),
            score_riesgo_promedio=("score_riesgo", "mean"),
            roa_promedio=("roa", "mean"),
            endeudamiento_promedio=("endeudamiento", "mean"),
        )
        .reset_index()
    )
    fact_sector_risk["score_riesgo_promedio"] = fact_sector_risk["score_riesgo_promedio"].round(2)

    latest_period = fact_financial_kpis.sort_values(["ejercicio", "periodo_orden"]).tail(1)[
        ["ejercicio", "periodo"]
    ].iloc[0]
    latest = fact_financial_kpis[
        (fact_financial_kpis["ejercicio"] == latest_period["ejercicio"])
        & (fact_financial_kpis["periodo"] == latest_period["periodo"])
    ].copy()

    dashboard_summary = pd.DataFrame(
        [
            {
                "periodo_actual": f"{latest_period['ejercicio']}-{latest_period['periodo']}",
                "empresas": latest["rpj"].nunique(),
                "sectores": latest["tipo_sector"].replace("", pd.NA).dropna().nunique(),
                "score_riesgo_promedio": round(latest["score_riesgo"].mean(), 2),
                "empresas_riesgo_alto": int((latest["nivel_riesgo"] == "Alto").sum()),
                "activo_total": latest["activo_total"].sum(),
                "pasivo_total": latest["pasivo_total"].sum(),
            }
        ]
    )

    outputs = {
        "dim_empresa": dim_empresa,
        "fact_financial_kpis": fact_financial_kpis,
        "fact_sector_risk": fact_sector_risk,
        "dashboard_summary": dashboard_summary,
    }

    for name, df in outputs.items():
        df.to_csv(GOLD_DIR / f"{name}.csv", index=False, encoding="utf-8-sig")

    bcrp_path = SILVER_DIR / "bcrp_series_wide.csv"
    if bcrp_path.exists():
        bcrp = pd.read_csv(bcrp_path)
        bcrp.to_csv(GOLD_DIR / "fact_macro_bcrp.csv", index=False, encoding="utf-8-sig")
        outputs["fact_macro_bcrp"] = bcrp

    return outputs


def run_gold() -> dict[str, int]:
    outputs = build_gold()
    return {name: len(df) for name, df in outputs.items()}
