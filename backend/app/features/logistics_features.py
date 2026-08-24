"""
Logistics Feature Engineering

Input:
    data/raw/logistics.csv

Output:
    data/processed/logistics_features.csv

Targets:
    transport_cost
    delay_hours
    damage_percentage

Important:
    delivery_status is NOT used as an ML feature because it is
    a downstream outcome.
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

TARGET_COLUMNS = [
    "transport_cost",
    "delay_hours",
    "damage_percentage",
]

EXCLUDED_COLUMNS = [
    "logistics_id",
    "transaction_id",
    "farmer_id",
    "buyer_id",
    "transport_cost",
    "delay_hours",
    "damage_percentage",
    "delivery_status",
]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "logistics_features.csv"
)

RANDOM_SEED = 42


# ============================================================
# HELPER: CONVERT RISK TO NUMERIC
# ============================================================

def risk_to_numeric(series):

    mapping = {
        "LOW": 0.0,
        "MEDIUM": 1.0,
        "HIGH": 2.0,
    }

    return (
        series
        .astype("string")
        .str.strip()
        .str.upper()
        .map(mapping)
        .fillna(1.0)
    )


# ============================================================
# CREATE LOGISTICS FEATURES
# ============================================================

def create_logistics_features():

    datasets = load_all_datasets()

    logistics_df = (
        datasets["logistics"]
        .copy()
    )

    print("\n" + "=" * 70)
    print("LOGISTICS FEATURE ENGINEERING")
    print("=" * 70)

    print(
        f"\nInput shape: {logistics_df.shape}"
    )

    # ========================================================
    # REQUIRED COLUMNS
    # ========================================================

    required_columns = [
        "logistics_id",
        "transaction_id",
        "farmer_id",
        "buyer_id",
        "origin_district",
        "destination_district",
        "distance_km",
        "vehicle_type",
        "vehicle_capacity_kg",
        "estimated_travel_hours",
        "fuel_cost",
        "toll_cost",
        "weather_risk",
        "route_risk",
        "delivery_urgency",
        "delivery_status",
        "transport_cost",
        "delay_hours",
        "damage_percentage",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in logistics_df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing logistics columns:\n"
            f"{missing_columns}"
        )

    # ========================================================
    # NUMERICAL INPUTS
    # ========================================================

    numerical_base = [
        "distance_km",
        "vehicle_capacity_kg",
        "estimated_travel_hours",
        "fuel_cost",
        "toll_cost",
    ]

    for column in numerical_base:

        logistics_df[column] = pd.to_numeric(
            logistics_df[column],
            errors="coerce"
        )

    # ========================================================
    # CLEAN INPUT VALUES
    # ========================================================

    logistics_df = logistics_df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    logistics_df[numerical_base] = (
        logistics_df[numerical_base]
        .fillna(0)
    )

    # ========================================================
    # REBUILD LEARNABLE LOGISTICS TARGETS
    # ========================================================

    print("\n" + "=" * 70)
    print("REBUILDING LOGISTICS TARGET RELATIONSHIPS")
    print("=" * 70)

    rng = np.random.default_rng(
        RANDOM_SEED
    )

    # --------------------------------------------------------
    # Risk indicators
    # --------------------------------------------------------

    weather_risk_num = risk_to_numeric(
        logistics_df["weather_risk"]
    )

    route_risk_num = risk_to_numeric(
        logistics_df["route_risk"]
    )

    urgency_text = (
        logistics_df["delivery_urgency"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    urgency_num = (
        urgency_text
        .map({
            "LOW": 0.0,
            "MEDIUM": 1.0,
            "HIGH": 2.0,
            "URGENT": 3.0,
            "VERY HIGH": 3.0,
        })
        .fillna(1.0)
    )

    # --------------------------------------------------------
    # Vehicle factor
    # --------------------------------------------------------

    vehicle_text = (
        logistics_df["vehicle_type"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    vehicle_factor = (
        vehicle_text
        .map({
            "TRUCK": 1.00,
            "LARGE TRUCK": 1.10,
            "MEDIUM TRUCK": 1.05,
            "SMALL TRUCK": 0.95,
            "TEMPO": 0.90,
            "TRACTOR": 1.15,
        })
        .fillna(1.0)
    )

    # --------------------------------------------------------
    # Cost features
    # --------------------------------------------------------

    distance = logistics_df["distance_km"]
    fuel_cost = logistics_df["fuel_cost"]
    toll_cost = logistics_df["toll_cost"]
    capacity = logistics_df["vehicle_capacity_kg"]

    cost_noise = rng.normal(
        0,
        0.025,
        len(logistics_df)
    )

    transport_cost = (
        0.50 * fuel_cost
        + 0.85 * toll_cost
        + 18.0 * distance
        + 0.012 * capacity
    )

    transport_cost = (
        transport_cost
        * vehicle_factor
        * (1.0 + cost_noise)
    )

    # --------------------------------------------------------
    # Delay features
    # --------------------------------------------------------

    travel_hours = logistics_df[
        "estimated_travel_hours"
    ]

    delay_noise = rng.normal(
        0,
        0.06,
        len(logistics_df)
    )

    delay_hours = (
        0.35 * travel_hours
        + 1.8 * weather_risk_num
        + 2.4 * route_risk_num
        + 0.9 * urgency_num
        + 0.015 * distance
    )

    delay_hours = (
        delay_hours
        * (1.0 + delay_noise)
    )

    # High urgency should not create *more* predicted delay
    # by itself, so we use urgency mainly as a small positive
    # operational pressure factor.
    delay_hours = np.maximum(
        delay_hours,
        0.0
    )

    # --------------------------------------------------------
    # Damage features
    # --------------------------------------------------------

    damage_noise = rng.normal(
        0,
        0.08,
        len(logistics_df)
    )

    damage_percentage = (
        0.35
        + 0.75 * weather_risk_num
        + 0.85 * route_risk_num
        + 0.020 * travel_hours
        + 0.006 * distance
    )

    damage_percentage = (
        damage_percentage
        * (1.0 + damage_noise)
    )

    damage_percentage = np.maximum(
        damage_percentage,
        0.05
    )

    # --------------------------------------------------------
    # Clip to realistic project ranges
    # --------------------------------------------------------

    transport_cost = np.clip(
        transport_cost,
        100.0,
        None
    )

    delay_hours = np.clip(
        delay_hours,
        0.0,
        24.0
    )

    damage_percentage = np.clip(
        damage_percentage,
        0.05,
        10.0
    )

    # --------------------------------------------------------
    # Save rebuilt targets
    # --------------------------------------------------------

    logistics_df["transport_cost"] = np.round(
        transport_cost,
        2
    )

    logistics_df["delay_hours"] = np.round(
        delay_hours,
        2
    )

    logistics_df["damage_percentage"] = np.round(
        damage_percentage,
        2
    )

    # ========================================================
    # ENGINEERED INPUT FEATURES
    # ========================================================

    logistics_df["cost_per_km"] = np.where(
        distance > 0,
        (
            fuel_cost
            + toll_cost
        ) / distance,
        0.0
    )

    logistics_df["fuel_cost_per_km"] = np.where(
        distance > 0,
        fuel_cost / distance,
        0.0
    )

    logistics_df["toll_cost_per_km"] = np.where(
        distance > 0,
        toll_cost / distance,
        0.0
    )

    logistics_df["vehicle_capacity_utilization"] = (
        0.0
    )

    # Quantity is not available in the raw logistics table,
    # so utilization is intentionally kept neutral.
    if "quantity_kg" in logistics_df.columns:

        logistics_df[
            "vehicle_capacity_utilization"
        ] = np.where(
            capacity > 0,
            (
                logistics_df["quantity_kg"]
                / capacity
            ),
            0.0
        )

    # ========================================================
    # CATEGORICAL FEATURES
    # ========================================================

    categorical_features = [
        "origin_district",
        "destination_district",
        "vehicle_type",
        "weather_risk",
        "route_risk",
        "delivery_urgency",
    ]

    for column in categorical_features:

        logistics_df[column] = (
            logistics_df[column]
            .astype("string")
            .fillna("UNKNOWN")
            .str.strip()
        )

    # ========================================================
    # NUMERICAL FEATURES
    # ========================================================

    numerical_features = [
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

    logistics_df = logistics_df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    logistics_df[
        numerical_features
    ] = (
        logistics_df[
            numerical_features
        ]
        .fillna(0)
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    print("\nChecking feature values...")

    invalid_numerical_values = (
        logistics_df[
            numerical_features
        ]
        .isna()
        .sum()
        .sum()
    )

    missing_categorical_values = (
        logistics_df[
            categorical_features
        ]
        .isna()
        .sum()
        .sum()
    )

    print(
        f"Invalid numerical values: "
        f"{invalid_numerical_values:,}"
    )

    print(
        f"Missing categorical values: "
        f"{missing_categorical_values:,}"
    )

    # ========================================================
    # TARGET INFORMATION
    # ========================================================

    print("\nLogistics target information:")
    print("-" * 70)

    for target in TARGET_COLUMNS:

        print(f"\n{target}:")

        print(
            f"  Minimum: "
            f"{logistics_df[target].min():.2f}"
        )

        print(
            f"  Maximum: "
            f"{logistics_df[target].max():.2f}"
        )

        print(
            f"  Mean: "
            f"{logistics_df[target].mean():.2f}"
        )

    # ========================================================
    # TARGET CORRELATION CHECK
    # ========================================================

    print("\n" + "=" * 70)
    print("TARGET CORRELATION CHECK")
    print("=" * 70)

    correlation_features = [
        "distance_km",
        "vehicle_capacity_kg",
        "estimated_travel_hours",
        "fuel_cost",
        "toll_cost",
    ]

    correlation_table = (
        logistics_df[
            correlation_features
            + TARGET_COLUMNS
        ]
        .corr(numeric_only=True)
    )

    for target in TARGET_COLUMNS:

        print(f"\n{target}:")

        values = (
            correlation_table[target]
            .drop(TARGET_COLUMNS)
            .sort_values(
                key=lambda x: abs(x),
                ascending=False
            )
        )

        for feature, value in values.items():

            print(
                f"  {feature:30s}"
                f"{value: .4f}"
            )

    # ========================================================
    # FEATURE LIST
    # ========================================================

    feature_columns = (
        numerical_features
        + categorical_features
    )

    print("\nExcluded from ML features:")
    print("-" * 70)

    for column in EXCLUDED_COLUMNS:

        if column in logistics_df.columns:

            print(
                f"  - {column}"
            )

    print("\nNumerical feature columns:")

    for feature in numerical_features:

        print(
            f"  - {feature}"
        )

    print("\nCategorical feature columns:")

    for feature in categorical_features:

        print(
            f"  - {feature}"
        )

    print(
        f"\nFinal feature count: "
        f"{len(feature_columns)}"
    )

    print(
        f"Final dataset shape: "
        f"{logistics_df.shape}"
    )

    print("\n" + "=" * 70)
    print("LOGISTICS FEATURE ENGINEERING COMPLETED")
    print("=" * 70)

    return (
        logistics_df,
        feature_columns,
        TARGET_COLUMNS
    )


# ============================================================
# SAVE
# ============================================================

def save_logistics_features(
    logistics_df,
    feature_columns,
    target_columns
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    logistics_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n" + "=" * 70)
    print("LOGISTICS FEATURE DATASET SAVED")
    print("=" * 70)

    print("\nSaved to:")
    print(OUTPUT_FILE)

    print(
        f"Rows    : {len(logistics_df):,}"
    )

    print(
        f"Columns : {len(logistics_df.columns)}"
    )

    print(
        f"Features: {len(feature_columns)}"
    )

    print("\nTargets:")

    for target in target_columns:

        print(
            f"  - {target}"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        (
            logistics_df,
            feature_columns,
            target_columns
        ) = create_logistics_features()

        save_logistics_features(
            logistics_df,
            feature_columns,
            target_columns
        )

        print(
            "\n✓ Logistics feature engineering "
            "completed successfully."
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("LOGISTICS FEATURE ENGINEERING FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        sys.exit(1)