"""
Cost Estimation Feature Engineering

Sources:
    farmers.csv
    transactions.csv
    logistics.csv

Output:
    data/processed/cost_features.csv

Target:
    estimated_total_cost

Target definition:
    estimated_production_cost + transport_cost

Important:
    transport_cost is used ONLY to construct the target.
    It is NOT used as an ML input feature.
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

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "cost_features.csv"
)

TARGET_COLUMN = "estimated_total_cost"


# ============================================================
# CREATE COST FEATURES
# ============================================================

def create_cost_features():

    datasets = load_all_datasets()

    farmers = datasets["farmers"].copy()
    transactions = datasets["transactions"].copy()
    logistics = datasets["logistics"].copy()

    print("\n" + "=" * 70)
    print("COST ESTIMATION FEATURE ENGINEERING")
    print("=" * 70)

    print("\nInput datasets:")

    print(
        f"Farmers      : {farmers.shape}"
    )

    print(
        f"Transactions : {transactions.shape}"
    )

    print(
        f"Logistics    : {logistics.shape}"
    )

    # ========================================================
    # REQUIRED RAW FARMER COLUMNS
    # ========================================================

    required_farmer = [
        "farmer_id",
        "district",
        "market",
        "crop",
        "farm_size_acres",
        "expected_quantity_kg",
        "production_cost",
    ]

    required_transaction = [
        "transaction_id",
        "farmer_id",
        "quantity_kg",
    ]

    required_logistics = [
        "transaction_id",
        "distance_km",
        "vehicle_capacity_kg",
        "estimated_travel_hours",
        "fuel_cost",
        "toll_cost",
        "vehicle_type",
        "weather_risk",
        "route_risk",
        "delivery_urgency",
        "transport_cost",
    ]

    # ========================================================
    # COLUMN VALIDATION
    # ========================================================

    missing_farmer = [
        column
        for column in required_farmer
        if column not in farmers.columns
    ]

    missing_transaction = [
        column
        for column in required_transaction
        if column not in transactions.columns
    ]

    missing_logistics = [
        column
        for column in required_logistics
        if column not in logistics.columns
    ]

    if missing_farmer:
        raise ValueError(
            "Missing farmer columns:\n"
            f"{missing_farmer}"
        )

    if missing_transaction:
        raise ValueError(
            "Missing transaction columns:\n"
            f"{missing_transaction}"
        )

    if missing_logistics:
        raise ValueError(
            "Missing logistics columns:\n"
            f"{missing_logistics}"
        )

    # ========================================================
    # SELECT REQUIRED COLUMNS
    # ========================================================

    farmers = farmers[
        required_farmer
    ].copy()

    transactions = transactions[
        required_transaction
    ].copy()

    logistics = logistics[
        required_logistics
    ].copy()

    # ========================================================
    # NUMERIC CONVERSION
    # ========================================================

    farmer_numeric = [
        "farm_size_acres",
        "expected_quantity_kg",
        "production_cost",
    ]

    transaction_numeric = [
        "quantity_kg",
    ]

    logistics_numeric = [
        "distance_km",
        "vehicle_capacity_kg",
        "estimated_travel_hours",
        "fuel_cost",
        "toll_cost",
        "transport_cost",
    ]

    for column in farmer_numeric:

        farmers[column] = pd.to_numeric(
            farmers[column],
            errors="coerce"
        )

    for column in transaction_numeric:

        transactions[column] = pd.to_numeric(
            transactions[column],
            errors="coerce"
        )

    for column in logistics_numeric:

        logistics[column] = pd.to_numeric(
            logistics[column],
            errors="coerce"
        )

    # ========================================================
    # DERIVE PRODUCTION COST PER KG
    # ========================================================

    farmers["production_cost_per_kg"] = np.where(
        farmers["expected_quantity_kg"] > 0,
        farmers["production_cost"]
        /
        farmers["expected_quantity_kg"],
        np.nan
    )

    # ========================================================
    # MERGE TRANSACTION + FARMER
    # ========================================================

    cost_df = transactions.merge(
        farmers,
        on="farmer_id",
        how="left",
        validate="many_to_one"
    )

    print(
        f"\nAfter farmer merge: "
        f"{cost_df.shape}"
    )

    # ========================================================
    # MERGE LOGISTICS
    # ========================================================

    cost_df = cost_df.merge(
        logistics,
        on="transaction_id",
        how="inner",
        validate="one_to_one"
    )

    print(
        f"After logistics merge: "
        f"{cost_df.shape}"
    )

    # ========================================================
    # REMOVE MISSING CORE VALUES
    # ========================================================

    core_columns = [
        "quantity_kg",
        "production_cost_per_kg",
        "distance_km",
        "vehicle_capacity_kg",
        "estimated_travel_hours",
        "fuel_cost",
        "toll_cost",
        "transport_cost",
    ]

    missing_core = (
        cost_df[core_columns]
        .isna()
        .any(axis=1)
        .sum()
    )

    print(
        f"\nRows with missing core cost inputs: "
        f"{missing_core:,}"
    )

    cost_df = (
        cost_df
        .dropna(subset=core_columns)
        .reset_index(drop=True)
    )

    # ========================================================
    # ESTIMATED PRODUCTION COST
    # ========================================================

    cost_df[
        "estimated_production_cost"
    ] = (
        cost_df["quantity_kg"]
        *
        cost_df["production_cost_per_kg"]
    )

    # ========================================================
    # TOTAL COST TARGET
    # ========================================================

    cost_df[
        TARGET_COLUMN
    ] = (
        cost_df["estimated_production_cost"]
        +
        cost_df["transport_cost"]
    )

    # ========================================================
    # ENGINEERED LOGISTICS COST FEATURES
    # ========================================================

    cost_df["cost_per_km"] = np.where(
        cost_df["distance_km"] > 0,

        (
            cost_df["fuel_cost"]
            +
            cost_df["toll_cost"]
        )
        /
        cost_df["distance_km"],

        0.0
    )

    cost_df["fuel_cost_per_km"] = np.where(
        cost_df["distance_km"] > 0,

        cost_df["fuel_cost"]
        /
        cost_df["distance_km"],

        0.0
    )

    cost_df["toll_cost_per_km"] = np.where(
        cost_df["distance_km"] > 0,

        cost_df["toll_cost"]
        /
        cost_df["distance_km"],

        0.0
    )

    cost_df[
        "vehicle_capacity_utilization"
    ] = np.where(
        cost_df["vehicle_capacity_kg"] > 0,

        cost_df["quantity_kg"]
        /
        cost_df["vehicle_capacity_kg"],

        0.0
    )

    # ========================================================
    # CATEGORICAL FEATURES
    # ========================================================

    categorical_features = [
        "district",
        "market",
        "crop",
        "vehicle_type",
        "weather_risk",
        "route_risk",
        "delivery_urgency",
    ]

    for column in categorical_features:

        cost_df[column] = (
            cost_df[column]
            .astype("string")
            .fillna("UNKNOWN")
            .str.strip()
        )

    # ========================================================
    # NUMERICAL FEATURES
    # ========================================================

    numerical_features = [
        "quantity_kg",
        "production_cost_per_kg",
        "farm_size_acres",
        "distance_km",
        "vehicle_capacity_kg",
        "estimated_travel_hours",
        "fuel_cost",
        "toll_cost",
        "cost_per_km",
        "fuel_cost_per_km",
        "toll_cost_per_km",
        "vehicle_capacity_utilization",
    ]

    # ========================================================
    # REMOVE INVALID VALUES
    # ========================================================

    cost_df = cost_df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    cost_df[
        numerical_features
    ] = (
        cost_df[
            numerical_features
        ]
        .fillna(0)
    )

    # ========================================================
    # FINAL FEATURE LIST
    # ========================================================

    feature_columns = (
        numerical_features
        +
        categorical_features
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    invalid_numerical_values = (
        cost_df[
            numerical_features
        ]
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
        .isna()
        .sum()
        .sum()
    )

    missing_target = (
        cost_df[TARGET_COLUMN]
        .isna()
        .sum()
    )

    print(
        f"\nInvalid numerical values: "
        f"{invalid_numerical_values:,}"
    )

    print(
        f"Missing target values: "
        f"{missing_target:,}"
    )

    if invalid_numerical_values > 0:

        raise ValueError(
            "Invalid numerical values "
            "found in cost features."
        )

    if missing_target > 0:

        raise ValueError(
            "Missing cost estimation targets."
        )

    # ========================================================
    # TARGET INFORMATION
    # ========================================================

    print("\nCost target:")
    print("-" * 70)

    print(
        f"Target: "
        f"{TARGET_COLUMN}"
    )

    print(
        f"Minimum: "
        f"{cost_df[TARGET_COLUMN].min():.2f}"
    )

    print(
        f"Maximum: "
        f"{cost_df[TARGET_COLUMN].max():.2f}"
    )

    print(
        f"Mean: "
        f"{cost_df[TARGET_COLUMN].mean():.2f}"
    )

    # ========================================================
    # TARGET CORRELATION
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "TARGET CORRELATION CHECK"
    )

    print(
        "=" * 70
    )

    correlation_columns = [
        "quantity_kg",
        "production_cost_per_kg",
        "farm_size_acres",
        "distance_km",
        "vehicle_capacity_kg",
        "estimated_travel_hours",
        "fuel_cost",
        "toll_cost",
        TARGET_COLUMN,
    ]

    correlations = (
        cost_df[
            correlation_columns
        ]
        .corr(
            numeric_only=True
        )[TARGET_COLUMN]
        .drop(TARGET_COLUMN)
        .sort_values(
            key=lambda x: abs(x),
            ascending=False
        )
    )

    for feature, value in correlations.items():

        print(
            f"{feature:35s}"
            f"{value: .4f}"
        )

    # ========================================================
    # EXCLUDED COLUMNS
    # ========================================================

    excluded_columns = [
        "transaction_id",
        "farmer_id",
        "transport_cost",
        "estimated_production_cost",
        TARGET_COLUMN,
    ]

    print(
        "\nExcluded from ML features:"
    )

    print("-" * 70)

    for column in excluded_columns:

        if column in cost_df.columns:

            print(
                f"  - {column}"
            )

    # ========================================================
    # FINAL FEATURE INFORMATION
    # ========================================================

    print(
        "\nFinal feature count: "
        f"{len(feature_columns)}"
    )

    print(
        f"Final dataset shape: "
        f"{cost_df.shape}"
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "COST FEATURE ENGINEERING COMPLETED"
    )

    print(
        "=" * 70
    )

    return (
        cost_df,
        feature_columns,
        TARGET_COLUMN
    )


# ============================================================
# SAVE
# ============================================================

def save_cost_features(
    cost_df,
    feature_columns,
    target_column
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    cost_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "COST FEATURE DATASET SAVED"
    )

    print(
        "=" * 70
    )

    print("\nSaved to:")
    print(OUTPUT_FILE)

    print(
        f"Rows    : "
        f"{len(cost_df):,}"
    )

    print(
        f"Columns : "
        f"{len(cost_df.columns)}"
    )

    print(
        f"Features: "
        f"{len(feature_columns)}"
    )

    print(
        f"Target  : "
        f"{target_column}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        (
            cost_df,
            feature_columns,
            target_column
        ) = create_cost_features()

        save_cost_features(
            cost_df,
            feature_columns,
            target_column
        )

        print(
            "\n✓ Cost feature engineering "
            "completed successfully."
        )

    except Exception as error:

        print(
            "\n" + "=" * 70
        )

        print(
            "COST FEATURE ENGINEERING FAILED"
        )

        print(
            "=" * 70
        )

        print(
            f"\nError: {error}"
        )

        sys.exit(1)