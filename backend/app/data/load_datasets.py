from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


# ============================================================
# DATASET FILES
# ============================================================

DATASET_FILES = {
    "farmers": "farmers.csv",
    "buyers": "buyers.csv",
    "market_prices": "market_prices.csv",
    "historical_price_features": "historical_price_features.csv",
    "demand_arrivals": "demand_arrivals.csv",
    "transactions": "transactions.csv",
    "logistics": "logistics.csv",
    "crop_quality": "crop_quality.csv",
}


# ============================================================
# LOAD ALL DATASETS
# ============================================================

def load_all_datasets():
    datasets = {}

    print("\n" + "=" * 70)
    print("LOADING AGRICULTURE AI DATASETS")
    print("=" * 70)

    for dataset_name, filename in DATASET_FILES.items():

        file_path = RAW_DATA_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"\nDataset not found:\n{file_path}"
            )

        df = pd.read_csv(file_path)

        datasets[dataset_name] = df

        print(
            f"✓ {dataset_name:<30} "
            f"Rows: {len(df):>8,} | "
            f"Columns: {len(df.columns):>4}"
        )

    print("=" * 70)
    print("ALL 8 DATASETS LOADED SUCCESSFULLY")
    print("=" * 70)

    return datasets


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    datasets = load_all_datasets()

    print("\nDataset names:")
    for name in datasets:
        print(f" - {name}")