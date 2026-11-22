from pathlib import Path
import subprocess
import zipfile

import polars as pl

COMPETITION = "ieee-fraud-detection"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"
ZIP_PATH = BRONZE_DIR / f"{COMPETITION}.zip"


def download() -> None:
    if ZIP_PATH.exists():
        print(f"{ZIP_PATH} already exists. Skipping download.")
        return
    # make sure the folder exists
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    # download the data from Kaggle
    subprocess.run([
        "kaggle",
        "competitions",
        "download",
        "-c",
        COMPETITION,
        "-p",
        str(BRONZE_DIR),
    ], check=True)


def unzip() -> None:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(
            f"Zip file not found: {ZIP_PATH}. Run the download step first."
        )

    with zipfile.ZipFile(ZIP_PATH) as zf:
        names = zf.namelist()

        missing = [name for name in names if not (BRONZE_DIR / name).exists()]

        if not missing:
            print(f"All files from {ZIP_PATH} are already on disk.")
            return

        zf.extractall(BRONZE_DIR, members=missing)
        print(f"Extracted {len(missing)} of {len(names)} files to {BRONZE_DIR}: {missing}")


def convert_to_parquet() -> None:
    csv_files = sorted(BRONZE_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {BRONZE_DIR}")
    for csv_file in csv_files:
        parquet_file = csv_file.with_suffix(".parquet")
        if parquet_file.exists():
            print(f"{parquet_file} already exists. Skipping conversion.")
            continue
        pl.scan_csv(csv_file).sink_parquet(parquet_file)
        print(f"Converted {csv_file} to {parquet_file}")
    


def main() -> None:
    download()
    unzip()
    convert_to_parquet()


if __name__ == "__main__":
    main()