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


# ============================================================
# PRICE FEATURE ENGINEERING
# ============================================================

def create_price_features():

    datasets = load_all_datasets()

    price_df = datasets[
        "historical_price_features"
    ].copy()

    print("\n" + "=" * 70)
    print("PRICE FEATURE ENGINEERING")
    print("=" * 70)

    print(
        f"\nInput shape: {price_df.shape}"
    )

    # ========================================================
    # DATE CONVERSION
    # ========================================================

    price_df["date"] = pd.to_datetime(
        price_df["date"],
        errors="coerce"
    )

    # ========================================================
    # SORT CHRONOLOGICALLY
    # ========================================================

    group_columns = [
        "district",
        "market",
        "crop",
        "variety"
    ]

    price_df = price_df.sort_values(
        group_columns + ["date"]
    ).reset_index(drop=True)

    # ========================================================
    # CREATE FUTURE PRICE TARGET
    # ========================================================

    # The model predicts the next available modal price
    # for the same district + market + crop + variety.

    price_df["next_modal_price_per_quintal"] = (
        price_df
        .groupby(group_columns)[
            "modal_price_per_quintal"
        ]
        .shift(-1)
    )

    # ========================================================
    # REMOVE ROWS WITHOUT FUTURE TARGET
    # ========================================================

    before_target_removal = len(price_df)

    price_df = price_df.dropna(
        subset=[
            "next_modal_price_per_quintal"
        ]
    ).reset_index(drop=True)

    removed_rows = (
        before_target_removal - len(price_df)
    )

    print(
        f"\nRows removed because next price "
        f"is unavailable: {removed_rows:,}"
    )

    # ========================================================
    # DATE FEATURES
    # ========================================================

    price_df["year"] = (
        price_df["date"].dt.year
    )

    price_df["month"] = (
        price_df["date"].dt.month
    )

    price_df["day"] = (
        price_df["date"].dt.day
    )

    price_df["day_of_week"] = (
        price_df["date"].dt.dayofweek
    )

    price_df["day_of_year"] = (
        price_df["date"].dt.dayofyear
    )

    price_df["week_of_year"] = (
        price_df["date"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    price_df["is_weekend"] = (
        price_df["day_of_week"] >= 5
    ).astype(int)

    # ========================================================
    # PRICE RANGE FEATURES
    # ========================================================

    price_df["price_range"] = (
        price_df["max_price_per_quintal"]
        -
        price_df["min_price_per_quintal"]
    )

    price_df["price_range_percentage"] = (
        price_df["price_range"]
        /
        price_df[
            "modal_price_per_quintal"
        ].replace(0, pd.NA)
    ) * 100

    # ========================================================
    # CURRENT PRICE POSITION
    # ========================================================

    price_difference = (
        price_df["max_price_per_quintal"]
        -
        price_df["min_price_per_quintal"]
    ).replace(0, pd.NA)

    price_df["modal_price_position"] = (
        (
            price_df["modal_price_per_quintal"]
            -
            price_df["min_price_per_quintal"]
        )
        /
        price_difference
    )

    # ========================================================
    # PRICE / ARRIVAL RELATIONSHIP
    # ========================================================

    price_df["price_per_arrival"] = (
        price_df["modal_price_per_quintal"]
        /
        price_df[
            "arrival_quantity_tonnes"
        ].replace(0, pd.NA)
    )

    # ========================================================
    # IMPORTANT:
    # DO NOT CREATE next_price_change_percentage
    #
    # It would use:
    # next_modal_price_per_quintal
    #
    # which is our future target.
    # Therefore it would cause target leakage.
    # ========================================================

    # ========================================================
    # TARGET
    # ========================================================

    target_column = (
        "next_modal_price_per_quintal"
    )

    # ========================================================
    # EXCLUDE TARGET / IDENTIFIER / CURRENT TARGET
    # ========================================================

    excluded_columns = [
        "price_id",
        "date",
        "modal_price_per_quintal",
        "next_modal_price_per_quintal"
    ]

    feature_columns = [
        column
        for column in price_df.columns
        if column not in excluded_columns
    ]

    # ========================================================
    # CHECK FOR INVALID NUMERICAL VALUES
    # ========================================================

    print("\nChecking feature values...")

    numerical_features = price_df[
        feature_columns
    ].select_dtypes(
        include=["number"]
    )

    invalid_values = (
        numerical_features
        .replace(
            [float("inf"), float("-inf")],
            pd.NA
        )
        .isna()
        .sum()
        .sum()
    )

    print(
        f"Invalid numerical values: "
        f"{invalid_values:,}"
    )

    # ========================================================
    # TARGET INFORMATION
    # ========================================================

    print("\nTarget:")
    print("-" * 70)

    print(
        f"Target column: {target_column}"
    )

    print(
        f"Target minimum: "
        f"{price_df[target_column].min():.2f}"
    )

    print(
        f"Target maximum: "
        f"{price_df[target_column].max():.2f}"
    )

    print(
        f"Target mean: "
        f"{price_df[target_column].mean():.2f}"
    )

    # ========================================================
    # EXCLUDED COLUMNS
    # ========================================================

    print("\nExcluded from ML features:")
    print("-" * 70)

    for column in excluded_columns:

        if column in price_df.columns:

            print(f"  - {column}")

    # ========================================================
    # FINAL FEATURE COLUMNS
    # ========================================================

    print("\nFinal feature columns:")
    print("-" * 70)

    for column in feature_columns:

        print(f"  - {column}")

    print(
        f"\nFinal feature count: "
        f"{len(feature_columns)}"
    )

    print(
        f"Final dataset shape: "
        f"{price_df.shape}"
    )

    print("\n" + "=" * 70)
    print("PRICE FEATURE ENGINEERING COMPLETED")
    print("=" * 70)

    return (
        price_df,
        feature_columns,
        target_column
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    price_df, feature_columns, target_column = (
        create_price_features()
    )

    print(
        "\nPrice feature engineering test completed."
    )

    # ========================================================
    # SAVE ENGINEERED PRICE DATASET
    # ========================================================

    project_root = Path(__file__).resolve().parents[3]

    processed_dir = (
        project_root
        / "data"
        / "processed"
    )

    processed_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        processed_dir
        / "price_features.csv"
    )

    price_df.to_csv(
        output_path,
        index=False
    )

    print("\n" + "=" * 70)
    print("PRICE FEATURE DATASET SAVED")
    print("=" * 70)

    print(f"\nSaved to:")
    print(output_path)

    print(
        f"Rows    : {len(price_df):,}"
    )

    print(
        f"Columns : {len(price_df.columns)}"
    )

    print("\nPrice feature engineering test completed.")