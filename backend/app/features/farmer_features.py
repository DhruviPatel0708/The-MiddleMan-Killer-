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
# FARMER FEATURE ENGINEERING
# ============================================================

def create_farmer_features():

    datasets = load_all_datasets()

    farmer_df = datasets["farmers"].copy()

    print("\n" + "=" * 70)
    print("FARMER FEATURE ENGINEERING")
    print("=" * 70)

    print(
        f"\nInput shape: {farmer_df.shape}"
    )

    # ========================================================
    # IDENTIFIERS
    # ========================================================

    identifier_columns = [
        "farmer_id",
        "farmer_name"
    ]

    # ========================================================
    # DATE COLUMNS
    # ========================================================

    date_columns = [
        "sowing_date",
        "expected_harvest_date",
        "preferred_selling_date"
    ]

    # ========================================================
    # DATE CONVERSION
    # ========================================================

    for column in date_columns:

        farmer_df[column] = pd.to_datetime(
            farmer_df[column],
            errors="coerce"
        )

    # ========================================================
    # DATE-BASED FEATURES
    # ========================================================

    farmer_df["days_to_expected_harvest"] = (
        farmer_df["expected_harvest_date"]
        -
        farmer_df["sowing_date"]
    ).dt.days

    farmer_df["days_to_preferred_selling"] = (
        farmer_df["preferred_selling_date"]
        -
        farmer_df["expected_harvest_date"]
    ).dt.days

    farmer_df["sowing_month"] = (
        farmer_df["sowing_date"].dt.month
    )

    farmer_df["harvest_month"] = (
        farmer_df["expected_harvest_date"].dt.month
    )

    # ========================================================
    # PRODUCTION FEATURES
    # ========================================================

    farmer_df["production_cost_per_kg"] = 0.0

    valid_quantity = (
        farmer_df["expected_quantity_kg"] > 0
    )

    farmer_df.loc[
        valid_quantity,
        "production_cost_per_kg"
    ] = (
        farmer_df.loc[
            valid_quantity,
            "production_cost"
        ]
        /
        farmer_df.loc[
            valid_quantity,
            "expected_quantity_kg"
        ]
    )

    # ========================================================
    # STORAGE CAPACITY UTILIZATION
    # ========================================================

    farmer_df["expected_quantity_to_storage_ratio"] = 0.0

    valid_storage = (
        farmer_df["storage_capacity_kg"] > 0
    )

    farmer_df.loc[
        valid_storage,
        "expected_quantity_to_storage_ratio"
    ] = (
        farmer_df.loc[
            valid_storage,
            "expected_quantity_kg"
        ]
        /
        farmer_df.loc[
            valid_storage,
            "storage_capacity_kg"
        ]
    )

    # ========================================================
    # EXCLUDED COLUMNS
    # ========================================================

    excluded_columns = (
        identifier_columns
        +
        date_columns
    )

    # ========================================================
    # FEATURE COLUMNS
    # ========================================================

    feature_columns = [
        column
        for column in farmer_df.columns
        if column not in excluded_columns
    ]

    # ========================================================
    # NUMERICAL FEATURES
    # ========================================================

    numerical_columns = [
        column
        for column in feature_columns
        if pd.api.types.is_numeric_dtype(
            farmer_df[column]
        )
    ]

    # ========================================================
    # CATEGORICAL FEATURES
    # ========================================================

    categorical_columns = [
        "district",
        "market",
        "crop",
        "variety",
        "irrigation_type",
        "storage_available",
        "quality_grade"
    ]

    categorical_columns = [
        column
        for column in categorical_columns
        if column in farmer_df.columns
    ]

    # ========================================================
    # CHECK INVALID NUMERICAL VALUES
    # ========================================================

    print("\nChecking feature values...")

    numerical_features = farmer_df[
        numerical_columns
    ].copy()

    numerical_features = numerical_features.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    invalid_values = (
        numerical_features
        .isna()
        .sum()
        .sum()
    )

    print(
        f"Invalid numerical values: "
        f"{invalid_values:,}"
    )

    # ========================================================
    # FARMER INFORMATION
    # ========================================================

    print("\nCrop distribution:")
    print("-" * 70)

    print(
        farmer_df["crop"]
        .value_counts()
        .to_string()
    )

    print("\nQuality grade distribution:")
    print("-" * 70)

    print(
        farmer_df["quality_grade"]
        .value_counts()
        .to_string()
    )

    print("\nStorage availability:")
    print("-" * 70)

    print(
        farmer_df["storage_available"]
        .value_counts()
        .to_string()
    )

    # ========================================================
    # EXCLUDED COLUMNS
    # ========================================================

    print("\nExcluded from ML features:")
    print("-" * 70)

    for column in excluded_columns:

        if column in farmer_df.columns:

            print(f"  - {column}")

    # ========================================================
    # NUMERICAL FEATURES
    # ========================================================

    print("\nNumerical feature columns:")
    print("-" * 70)

    for column in numerical_columns:

        print(f"  - {column}")

    # ========================================================
    # CATEGORICAL FEATURES
    # ========================================================

    print("\nCategorical feature columns:")
    print("-" * 70)

    for column in categorical_columns:

        print(f"  - {column}")

    # ========================================================
    # SANITY CHECK
    # ========================================================

    if invalid_values != 0:

        raise ValueError(
            "Invalid numerical values remain "
            "after farmer feature engineering."
        )

    # ========================================================
    # FINAL INFORMATION
    # ========================================================

    print(
        f"\nFinal feature count: "
        f"{len(feature_columns)}"
    )

    print(
        f"Final dataset shape: "
        f"{farmer_df.shape}"
    )

    print("\n" + "=" * 70)
    print("FARMER FEATURE ENGINEERING COMPLETED")
    print("=" * 70)

    return (
        farmer_df,
        feature_columns
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    farmer_df, feature_columns = (
        create_farmer_features()
    )

    print(
        "\nFarmer feature engineering test completed."
    )