from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "data" / "gold"


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    kpis = pd.read_csv(GOLD / "fact_financial_kpis.csv")
    sector = pd.read_csv(GOLD / "fact_sector_risk.csv")
    summary = pd.read_csv(GOLD / "dashboard_summary.csv")
    macro = pd.read_csv(GOLD / "fact_macro_bcrp.csv", parse_dates=["fecha"])
    coverage_path = GOLD / "source_coverage.csv"
    coverage = pd.read_csv(coverage_path) if coverage_path.exists() else pd.DataFrame()
    return kpis, sector, summary, macro, coverage


st.set_page_config(page_title="SMV 360", layout="wide")
st.title("SMV 360 - Riesgo financiero corporativo")

kpis, sector, summary, macro, coverage = load_data()

periods = (
    kpis[["ejercicio", "periodo", "periodo_orden", "periodo_label"]]
    .drop_duplicates()
    .sort_values(["ejercicio", "periodo_orden"])
)
selected_period = st.sidebar.selectbox(
    "Periodo",
    periods["periodo_label"].tolist(),
    index=len(periods) - 1,
)

sector_options = ["Todos"] + sorted(kpis["tipo_sector"].dropna().unique().tolist())
selected_sector = st.sidebar.selectbox("Sector", sector_options)

view = kpis[kpis["periodo_label"] == selected_period].copy()
if selected_sector != "Todos":
    view = view[view["tipo_sector"] == selected_sector]

summary_now = summary.iloc[0]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Empresas", f"{view['rpj'].nunique():,.0f}")
col2.metric("Score promedio", f"{view['score_riesgo'].mean():.2f}")
col3.metric("Riesgo alto", f"{(view['nivel_riesgo'] == 'Alto').sum():,.0f}")
col4.metric("Periodo base", str(summary_now["periodo_actual"]))

tab_risk, tab_sector, tab_macro, tab_sources, tab_table = st.tabs(
    ["Radar de riesgo", "Analisis sectorial", "Contexto macro", "Fuentes", "Tabla gold"]
)

with tab_risk:
    left, right = st.columns([1.2, 1])

    with left:
        top_risk = view.sort_values("score_riesgo", ascending=False).head(20)
        fig = px.bar(
            top_risk,
            x="score_riesgo",
            y="nombre_empresa",
            color="nivel_riesgo",
            orientation="h",
            title="Top empresas por score de riesgo",
            labels={"score_riesgo": "Score", "nombre_empresa": "Empresa"},
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=650)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        risk_counts = view["nivel_riesgo"].value_counts().reset_index()
        risk_counts.columns = ["nivel_riesgo", "empresas"]
        fig = px.pie(
            risk_counts,
            values="empresas",
            names="nivel_riesgo",
            title="Distribucion de riesgo",
            hole=0.45,
        )
        st.plotly_chart(fig, use_container_width=True)

        fig = px.scatter(
            view,
            x="endeudamiento",
            y="roa",
            color="nivel_riesgo",
            size="activo_total",
            hover_name="nombre_empresa",
            title="Endeudamiento vs ROA",
        )
        st.plotly_chart(fig, use_container_width=True)

with tab_sector:
    sector_view = sector[
        (sector["ejercicio"].astype(str) + "-" + sector["periodo"]) == selected_period
    ].copy()
    if selected_sector != "Todos":
        sector_view = sector_view[sector_view["tipo_sector"] == selected_sector]

    fig = px.bar(
        sector_view.sort_values("score_riesgo_promedio", ascending=False),
        x="tipo_sector",
        y="score_riesgo_promedio",
        color="empresas",
        title="Score promedio por sector",
        labels={"tipo_sector": "Sector", "score_riesgo_promedio": "Score promedio"},
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.scatter(
        sector_view,
        x="endeudamiento_promedio",
        y="roa_promedio",
        size="empresas",
        color="score_riesgo_promedio",
        hover_name="tipo_sector",
        title="ROA promedio vs endeudamiento promedio por sector",
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_macro:
    macro_cols = [
        "tc_interbancario_venta",
        "tasa_referencia",
        "cobre_londres",
        "oro_londres",
        "ipc",
    ]
    selected_macro = st.multiselect(
        "Series BCRP",
        macro_cols,
        default=["tc_interbancario_venta", "tasa_referencia", "cobre_londres"],
    )
    if selected_macro:
        macro_long = macro[["fecha", *selected_macro]].melt(
            id_vars="fecha", var_name="serie", value_name="valor"
        )
        macro_long = macro_long.dropna(subset=["valor"])
        fig = px.line(
            macro_long,
            x="fecha",
            y="valor",
            color="serie",
            title="Series macroeconomicas BCRP",
        )
        st.plotly_chart(fig, use_container_width=True)

    annual_risk = (
        kpis.groupby("ejercicio", as_index=False)
        .agg(score_riesgo_promedio=("score_riesgo", "mean"), empresas=("rpj", "nunique"))
    )
    macro_annual = macro.groupby("anio", as_index=False).agg(
        tc_promedio=("tc_interbancario_venta", "mean"),
        tasa_promedio=("tasa_referencia", "mean"),
        cobre_promedio=("cobre_londres", "mean"),
    )
    joined = annual_risk.merge(macro_annual, left_on="ejercicio", right_on="anio", how="left")
    fig = px.line(
        joined,
        x="ejercicio",
        y=["score_riesgo_promedio", "tc_promedio", "tasa_promedio"],
        markers=True,
        title="Riesgo financiero vs variables macro promedio anual",
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_sources:
    st.subheader("Cobertura de fuentes oficiales")
    if coverage.empty:
        st.info("Ejecuta `python -m src.smv_bi.run_pipeline` para generar source_coverage.csv.")
    else:
        st.metric("Fuentes verificadas", coverage["source"].nunique())
        st.dataframe(
            coverage[["source", "dataset", "records", "status", "url"]],
            use_container_width=True,
            hide_index=True,
        )

with tab_table:
    st.subheader("Tabla gold")
    columns = [
        "nombre_empresa",
        "tipo_sector",
        "activo_total",
        "pasivo_total",
        "utilidad_neta",
        "roa",
        "endeudamiento",
        "margen_neto",
        "score_riesgo",
        "nivel_riesgo",
    ]
    st.dataframe(
        view[columns].sort_values("score_riesgo", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
