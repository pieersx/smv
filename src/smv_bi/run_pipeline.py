from .bronze import run_bronze
from .gold import run_gold
from .silver import run_silver


def main() -> None:
    bronze = run_bronze()
    print(f"Bronze: {bronze}")

    silver = run_silver()
    print(f"Silver: {silver}")

    gold = run_gold()
    print(f"Gold: {gold}")


if __name__ == "__main__":
    main()
