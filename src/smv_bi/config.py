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
