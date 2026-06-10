from .bronze import run_bronze
from .data_quality import run_data_quality
from .external_sources import run_external_sources
from .gold import run_gold
from .silver import run_silver


def main() -> None:
    bronze = run_bronze()
    print(f"Bronze: {bronze}")

    external = run_external_sources()
    print(f"External sources: {external}")

    silver = run_silver()
    print(f"Silver: {silver}")

    gold = run_gold()
    print(f"Gold: {gold}")

    quality = run_data_quality()
    print(f"Data quality: {quality}")


if __name__ == "__main__":
    main()
