import sys
from pathlib import Path

import pandas as pd


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

from backend.app.data.load_datasets import load_all_datasets

from backend.app.preprocessing.utils import (
    basic_cleaning,
    get_numerical_columns,
    get_categorical_columns
)


# ============================================================
# PRICE DATA PREPARATION
# ============================================================

def prepare_price_data():

    datasets = load_all_datasets()

    price_df = datasets[
        "historical_price_features"
    ].copy()

    print("\n" + "=" * 70)
    print("PRICE PREDICTION DATA PREPROCESSING")
    print("=" * 70)

    print(
        f"\nInitial shape: {price_df.shape}"
    )

    # --------------------------------------------------------
    # Basic cleaning
    # --------------------------------------------------------

    price_df = basic_cleaning(
        price_df,
        dataset_name="PRICE PREDICTION DATA",
        date_columns=["date"]
    )

    # --------------------------------------------------------
    # Sort by time and location
    # --------------------------------------------------------

    sort_columns = [
        "district",
        "market",
        "crop",
        "variety",
        "date"
    ]

    existing_sort_columns = [
        column
        for column in sort_columns
        if column in price_df.columns
    ]

    price_df = price_df.sort_values(
        existing_sort_columns
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Remove rows with invalid target
    # --------------------------------------------------------

    target_column = "modal_price_per_quintal"

    if target_column not in price_df.columns:
        raise ValueError(
            f"Target column '{target_column}' not found."
        )

    before_target_cleaning = len(price_df)

    price_df = price_df.dropna(
        subset=[target_column]
    )

    removed_target_rows = (
        before_target_cleaning - len(price_df)
    )

    print(
        f"\nRows removed due to missing target: "
        f"{removed_target_rows:,}"
    )

    # --------------------------------------------------------
    # Check target values
    # --------------------------------------------------------

    print("\nTarget:")
    print("-" * 70)

    print(
        f"Target column: {target_column}"
    )

    print(
        f"Target minimum: "
        f"{price_df[target_column].min()}"
    )

    print(
        f"Target maximum: "
        f"{price_df[target_column].max()}"
    )

    print(
        f"Target mean: "
        f"{price_df[target_column].mean():.2f}"
    )

    # --------------------------------------------------------
    # Feature columns
    # --------------------------------------------------------

    excluded_columns = [
        target_column,
        "price_id"
    ]

    feature_columns = [
        column
        for column in price_df.columns
        if column not in excluded_columns
    ]

    print("\nFeature columns:")
    print("-" * 70)

    for column in feature_columns:
        print(f"  - {column}")

    # --------------------------------------------------------
    # Numerical features
    # --------------------------------------------------------

    numerical_columns = get_numerical_columns(
        price_df[feature_columns]
    )

    print("\nNumerical feature columns:")
    print("-" * 70)

    for column in numerical_columns:
        print(f"  - {column}")

    # --------------------------------------------------------
    # Categorical features
    # --------------------------------------------------------

    categorical_columns = get_categorical_columns(
        price_df[feature_columns]
    )

    print("\nCategorical feature columns:")
    print("-" * 70)

    for column in categorical_columns:
        print(f"  - {column}")

    # --------------------------------------------------------
    # Final dataset information
    # --------------------------------------------------------

    print("\nFinal price dataset shape:")
    print(price_df.shape)

    print("\n" + "=" * 70)
    print("PRICE PREDICTION PREPROCESSING COMPLETED")
    print("=" * 70)

    return price_df


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    price_df = prepare_price_data()