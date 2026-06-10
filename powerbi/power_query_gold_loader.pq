// Power Query M - cargar tablas gold desde una carpeta local
// Cambiar RootPath si el proyecto esta en otra ubicacion.

let
    RootPath = "C:\Users\Pieers\Documents\smv-bi\data\gold\",

    LoadCsv = (FileName as text) =>
        let
            Source = Csv.Document(
                File.Contents(RootPath & FileName),
                [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
            ),
            PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
        in
            PromotedHeaders,

    fact_financial_kpis = LoadCsv("fact_financial_kpis.csv"),
    dim_empresa = LoadCsv("dim_empresa.csv"),
    fact_sector_risk = LoadCsv("fact_sector_risk.csv"),
    fact_macro_bcrp = LoadCsv("fact_macro_bcrp.csv"),
    fact_sbs_financial_system = LoadCsv("fact_sbs_financial_system.csv"),
    fact_inei_pbi_department = LoadCsv("fact_inei_pbi_department.csv"),
    fact_mef_state_enterprises = LoadCsv("fact_mef_state_enterprises.csv"),
    fact_bvl_market_snapshot = LoadCsv("fact_bvl_market_snapshot.csv"),
    source_coverage = LoadCsv("source_coverage.csv"),
    data_profile_tables = LoadCsv("data_profile_tables.csv"),
    data_quality_results = LoadCsv("data_quality_results.csv")
in
    [
        fact_financial_kpis = fact_financial_kpis,
        dim_empresa = dim_empresa,
        fact_sector_risk = fact_sector_risk,
        fact_macro_bcrp = fact_macro_bcrp,
        fact_sbs_financial_system = fact_sbs_financial_system,
        fact_inei_pbi_department = fact_inei_pbi_department,
        fact_mef_state_enterprises = fact_mef_state_enterprises,
        fact_bvl_market_snapshot = fact_bvl_market_snapshot,
        source_coverage = source_coverage,
        data_profile_tables = data_profile_tables,
        data_quality_results = data_quality_results
    ]
