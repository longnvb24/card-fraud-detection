from pathlib import Path

import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"
SILVER_DIR = PROJECT_ROOT / "data" / "silver"


def fix_identity_columns(identity: pl.LazyFrame) -> pl.LazyFrame:
    return identity.rename(lambda col: col.replace("id-", "id_") if col.startswith("id-") else col)


def join_tables(transactions: pl.LazyFrame, identity: pl.LazyFrame) -> pl.LazyFrame:
    return transactions.join(identity, on="TransactionID", how="left")


def validate(train: pl.LazyFrame, test: pl.LazyFrame) -> None:
    n_rows = train.select(pl.len()).collect().item()
    if n_rows != 590540:
        raise ValueError(f"The number of rows after join is not correct! Expected 590,540 rows, got {n_rows}")
    
    if set(train.collect_schema().names()) - set(test.collect_schema().names()) != {'isFraud'} \
        or set(test.collect_schema().names()) - set(train.collect_schema().names()) != set():
        raise ValueError("The column names after join is not correct!")


def main() -> None:
    # 1. scan the 4 bronze files
    train_tx = pl.scan_parquet(BRONZE_DIR / "train_transaction.parquet")
    train_id = pl.scan_parquet(BRONZE_DIR / "train_identity.parquet")
    test_tx = pl.scan_parquet(BRONZE_DIR / "test_transaction.parquet")
    test_id = pl.scan_parquet(BRONZE_DIR / "test_identity.parquet")

    # 2. fix identity column names (both train and test, to be safe)
    train_id = fix_identity_columns(train_id)
    test_id = fix_identity_columns(test_id)

    # 3. join each pair
    train = join_tables(train_tx, train_id)
    test = join_tables(test_tx, test_id)

    # 4. validate
    validate(train, test)

    # 5. create SILVER_DIR and write train.parquet and test.parquet
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    train.sink_parquet(SILVER_DIR / "train.parquet")
    test.sink_parquet(SILVER_DIR / "test.parquet")
    print(f"Silver files written to {SILVER_DIR}")


if __name__ == "__main__":
    main()