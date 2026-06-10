from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"

YEARS = list(range(2019, 2025))
PERIODS = ["1", "2", "3", "4", "A"]
SMV_INFO_TYPE = "I"

SMV_ENDPOINT = (
    "https://mvnet.smv.gob.pe/ws_OD_EEFF/"
    "WebServiceInfoFinanciera.asmx/obtener_EFData"
)

BCRP_SERIES = {
    "tc_interbancario_venta": "PD04638PD",
    "tasa_referencia": "PD12301MD",
    "cobre_londres": "PD04701XD",
    "oro_londres": "PD04704XD",
    "ipc": "PN01271PM",
}

BCRP_START = "2019-01-01"
BCRP_END = "2024-12-31"

BVL_DAILY_SUMMARY_URL = "https://documents.bvl.com.pe/pubdif/boldia/bolres.htm"

SBS_OPEN_DATA = {
    "sistema_financiero_estado_situacion": "https://www.sbs.gob.pe/Portals/0/jer/Datos%20Abiertos/v3/ESF_SF.zip",
    "sistema_financiero_estado_resultados": "https://www.sbs.gob.pe/Portals/0/jer/Datos%20Abiertos/v3/ER_SF.zip",
}

INEI_PBI_PERU_URL = "https://www.inei.gob.pe/media/MenuRecursivo/indices_tematicos/pbi_peru_16.xlsx"

MEF_BALANCE_EMPRESAS_ESTADO_RESOURCE_ID = "96ac0c23-abbc-4e28-b9f1-7977826f534b"
MEF_DATASTORE_URL = "https://api.datosabiertos.mef.gob.pe/DatosAbiertos/v1/datastore_search"
