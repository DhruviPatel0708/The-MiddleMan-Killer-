"""
Buyer Feature Engineering

Source:
    data/raw/buyers.csv

Output:
    data/processed/buyer_features.csv

Target:
    buyer_reliability_label
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORT DATA LOADER
# ============================================================

from backend.app.data.load_datasets import load_all_datasets


# ============================================================
# CONFIGURATION
# ============================================================

TARGET_COLUMN = "buyer_reliability_label"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "buyer_features.csv"
)


EXCLUDED_FROM_FEATURES = [
    "buyer_id",
    "buyer_name",
    "reliability_score",
    TARGET_COLUMN,
]


# ============================================================
# CREATE BUYER FEATURES
# ============================================================

def create_buyer_features():

    datasets = load_all_datasets()

    buyer_df = datasets["buyers"].copy()

    print("\n" + "=" * 70)
    print("BUYER FEATURE ENGINEERING")
    print("=" * 70)

    print(
        f"\nInput shape: {buyer_df.shape}"
    )

    # ========================================================
    # REQUIRED COLUMNS
    # ========================================================

    required_columns = [
        "buyer_id",
        "buyer_name",
        "buyer_type",
        "district",
        "market",
        "latitude",
        "longitude",
        "preferred_crop",
        "required_quantity_kg",
        "minimum_quantity_kg",
        "maximum_quantity_kg",
        "offered_price_per_kg",
        "minimum_quality_grade",
        "payment_terms_days",
        "storage_available",
        "buyer_rating",
        "total_previous_transactions",
        "successful_transactions",
        "cancelled_transactions",
        "late_payments",
        "average_payment_delay_days",
        "reliability_score",
        "buyer_reliability_label",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in buyer_df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing buyer columns:\n"
            f"{missing_columns}"
        )

    # ========================================================
    # DUPLICATES
    # ========================================================

    duplicate_rows = buyer_df.duplicated().sum()

    if duplicate_rows > 0:
        buyer_df = (
            buyer_df
            .drop_duplicates()
            .reset_index(drop=True)
        )

    # ========================================================
    # TARGET VALIDATION
    # ========================================================

    missing_target = (
        buyer_df[TARGET_COLUMN]
        .isna()
        .sum()
    )

    print("\nTarget missing values:")
    print("-" * 70)

    print(
        f"{TARGET_COLUMN}: {missing_target}"
    )

    if missing_target > 0:
        buyer_df = (
            buyer_df
            .dropna(subset=[TARGET_COLUMN])
            .reset_index(drop=True)
        )

    # ========================================================
    # TARGET DISTRIBUTION
    # ========================================================

    print("\nTarget distribution:")
    print("-" * 70)

    print(
        buyer_df[TARGET_COLUMN]
        .value_counts()
        .to_string()
    )

    # ========================================================
    # BASE NUMERICAL FEATURES
    # ========================================================

    base_numerical_columns = [
        "latitude",
        "longitude",
        "required_quantity_kg",
        "minimum_quantity_kg",
        "maximum_quantity_kg",
        "offered_price_per_kg",
        "payment_terms_days",
        "buyer_rating",
        "total_previous_transactions",
        "successful_transactions",
        "cancelled_transactions",
        "late_payments",
        "average_payment_delay_days",
    ]

    for column in base_numerical_columns:

        buyer_df[column] = pd.to_numeric(
            buyer_df[column],
            errors="coerce"
        )

    # ========================================================
    # ENGINEERED FEATURES
    # ========================================================

    total_transactions = (
        buyer_df["total_previous_transactions"]
    )

    buyer_df["successful_transaction_rate"] = np.where(
        total_transactions > 0,
        (
            buyer_df["successful_transactions"]
            / total_transactions
        ),
        0.0
    )

    buyer_df["cancellation_rate"] = np.where(
        total_transactions > 0,
        (
            buyer_df["cancelled_transactions"]
            / total_transactions
        ),
        0.0
    )

    buyer_df["late_payment_rate"] = np.where(
        total_transactions > 0,
        (
            buyer_df["late_payments"]
            / total_transactions
        ),
        0.0
    )

    buyer_df["successful_transactions_per_total"] = np.where(
        total_transactions > 0,
        (
            buyer_df["successful_transactions"]
            / total_transactions
        ),
        0.0
    )

    buyer_df["acceptable_quantity_range_kg"] = (
        buyer_df["maximum_quantity_kg"]
        - buyer_df["minimum_quantity_kg"]
    )

    buyer_df["required_quantity_to_max_ratio"] = np.where(
        buyer_df["maximum_quantity_kg"] > 0,
        (
            buyer_df["required_quantity_kg"]
            / buyer_df["maximum_quantity_kg"]
        ),
        0.0
    )

    buyer_df["payment_delay_to_terms_ratio"] = np.where(
        buyer_df["payment_terms_days"] > 0,
        (
            buyer_df["average_payment_delay_days"]
            / buyer_df["payment_terms_days"]
        ),
        0.0
    )

    # ========================================================
    # NUMERICAL FEATURE LIST
    # ========================================================

    engineered_numerical_columns = [
        "successful_transaction_rate",
        "cancellation_rate",
        "late_payment_rate",
        "successful_transactions_per_total",
        "acceptable_quantity_range_kg",
        "required_quantity_to_max_ratio",
        "payment_delay_to_terms_ratio",
    ]

    numerical_features = (
        base_numerical_columns
        + engineered_numerical_columns
    )

    # ========================================================
    # CLEAN NUMERICAL VALUES
    # ========================================================

    buyer_df = buyer_df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    buyer_df[numerical_features] = (
        buyer_df[numerical_features]
        .fillna(0)
    )

    # ========================================================
    # CATEGORICAL FEATURES
    # ========================================================

    categorical_features = [
        "buyer_type",
        "district",
        "market",
        "preferred_crop",
        "minimum_quality_grade",
        "storage_available",
    ]

    for column in categorical_features:

        buyer_df[column] = (
            buyer_df[column]
            .astype("string")
            .fillna("UNKNOWN")
            .str.strip()
        )

    # ========================================================
    # ML FEATURE LIST
    # ========================================================

    feature_columns = (
        numerical_features
        + categorical_features
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    print("\nChecking feature values...")

    invalid_numerical_values = (
        buyer_df[numerical_features]
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
        .isna()
        .sum()
        .sum()
    )

    missing_categorical_values = (
        buyer_df[categorical_features]
        .isna()
        .sum()
        .sum()
    )

    print(
        f"Invalid numerical values: "
        f"{invalid_numerical_values}"
    )

    print(
        f"Missing categorical values: "
        f"{missing_categorical_values}"
    )

    if invalid_numerical_values > 0:
        raise ValueError(
            "Invalid numerical values found."
        )

    if missing_categorical_values > 0:
        raise ValueError(
            "Missing categorical values found."
        )

    # ========================================================
    # EXCLUDED COLUMNS
    # ========================================================

    print("\nExcluded from ML features:")
    print("-" * 70)

    for column in EXCLUDED_FROM_FEATURES:

        if column in buyer_df.columns:
            print(
                f"  - {column}"
            )

    # ========================================================
    # NUMERICAL FEATURES
    # ========================================================

    print("\nNumerical feature columns:")

    for column in numerical_features:
        print(
            f"  - {column}"
        )

    # ========================================================
    # CATEGORICAL FEATURES
    # ========================================================

    print("\nCategorical feature columns:")

    for column in categorical_features:
        print(
            f"  - {column}"
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
        f"{buyer_df.shape}"
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "BUYER FEATURE ENGINEERING COMPLETED"
    )

    print(
        "=" * 70
    )

    return (
        buyer_df,
        feature_columns,
        TARGET_COLUMN
    )


# ============================================================
# SAVE
# ============================================================

def save_buyer_features(
    buyer_df,
    feature_columns,
    target_column
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    buyer_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "BUYER FEATURE DATASET SAVED"
    )

    print(
        "=" * 70
    )

    print("\nSaved to:")
    print(OUTPUT_FILE)

    print(
        f"Rows    : {len(buyer_df):,}"
    )

    print(
        f"Columns : {len(buyer_df.columns)}"
    )

    print(
        f"Features: {len(feature_columns)}"
    )

    print(
        f"Target  : {target_column}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        (
            buyer_df,
            feature_columns,
            target_column
        ) = create_buyer_features()

        save_buyer_features(
            buyer_df,
            feature_columns,
            target_column
        )

        print(
            "\n✓ Buyer feature engineering "
            "completed successfully."
        )

    except Exception as error:

        print(
            "\n" + "=" * 70
        )

        print(
            "BUYER FEATURE ENGINEERING FAILED"
        )

        print(
            "=" * 70
        )

        print(
            f"\nError: {error}"
        )

        sys.exit(1)