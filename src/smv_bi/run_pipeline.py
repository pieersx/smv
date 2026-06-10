from .bronze import run_bronze
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


if __name__ == "__main__":
    main()
