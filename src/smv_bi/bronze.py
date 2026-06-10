import json
from datetime import datetime, UTC
from pathlib import Path

import requests

from .config import (
    BCRP_END,
    BCRP_SERIES,
    BCRP_START,
    BRONZE_DIR,
    PERIODS,
    SMV_ENDPOINT,
    SMV_INFO_TYPE,
    YEARS,
)


def ensure_dirs() -> None:
    for path in [
        BRONZE_DIR / "smv" / "principales_cuentas",
        BRONZE_DIR / "bcrp" / "series",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def download_smv_principales_cuentas() -> list[Path]:
    paths: list[Path] = []
    body = {"_search": False, "rows": 100000, "page": 1, "sidx": "", "sord": "asc"}

    for year in YEARS:
        for period in PERIODS:
            params = {
                "ejercicio": year,
                "periodo": period,
                "tipo": SMV_INFO_TYPE,
                "estado": "IF",
            }
            response = requests.post(
                SMV_ENDPOINT,
                params=params,
                json=body,
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()
            payload["_metadata"] = {
                "source": "SMV Open Data - principales cuentas financieras",
                "url": response.url,
                "downloaded_at": datetime.now(UTC).isoformat(),
                "params": params,
            }

            path = (
                BRONZE_DIR
                / "smv"
                / "principales_cuentas"
                / f"ejercicio={year}_periodo={period}_tipo={SMV_INFO_TYPE}.json"
            )
            write_json(path, payload)
            paths.append(path)

    return paths


def download_bcrp_series() -> list[Path]:
    paths: list[Path] = []

    for name, code in BCRP_SERIES.items():
        url = (
            "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/"
            f"{code}/json/{BCRP_START}/{BCRP_END}/esp"
        )
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        payload = response.json()
        payload["_metadata"] = {
            "source": "BCRP API",
            "series_name": name,
            "series_code": code,
            "url": url,
            "downloaded_at": datetime.now(UTC).isoformat(),
        }

        path = BRONZE_DIR / "bcrp" / "series" / f"{name}_{code}.json"
        write_json(path, payload)
        paths.append(path)

    return paths


def run_bronze() -> dict[str, int]:
    ensure_dirs()
    smv_paths = download_smv_principales_cuentas()
    bcrp_paths = download_bcrp_series()
    return {
        "smv_files": len(smv_paths),
        "bcrp_files": len(bcrp_paths),
    }
