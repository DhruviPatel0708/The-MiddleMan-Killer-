"""
Transaction / Risk Feature Engineering

Purpose:
    Build learnable features for:

    1. payment_status
    2. delivery_status

Sources:
    transactions.csv
    buyers.csv
    logistics.csv

Important:
    Existing transaction_id, buyer_id, and farmer_id are preserved.

Targets are regenerated synthetically from pre-outcome information
so that the Risk models have meaningful predictive relationships.

Output:
    data/processed/transaction_features.csv
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
    / "transaction_features.csv"
)

RANDOM_SEED = 42


# ============================================================
# RISK HELPERS
# ============================================================

def normalize_rating(series):
    """
    Convert buyer rating to a 0-1 reliability scale.
    """

    rating = pd.to_numeric(
        series,
        errors="coerce"
    ).fillna(3.0)

    return np.clip(
        (rating - 1.0) / 4.0,
        0.0,
        1.0
    )


def risk_to_numeric(series):
    """
    Convert LOW / MEDIUM / HIGH to numeric risk.
    """

    mapping = {
        "LOW": 0.0,
        "MEDIUM": 1.0,
        "HIGH": 2.0
    }

    return (
        series
        .astype("string")
        .str.strip()
        .str.upper()
        .map(mapping)
        .fillna(1.0)
    )


def urgency_to_numeric(series):
    """
    Convert delivery urgency to numeric.
    """

    text = (
        series
        .astype("string")
        .str.strip()
        .str.upper()
    )

    return (
        text
        .map({
            "LOW": 0.0,
            "MEDIUM": 1.0,
            "HIGH": 2.0,
            "URGENT": 3.0,
            "VERY HIGH": 3.0
        })
        .fillna(1.0)
    )


# ============================================================
# CREATE TRANSACTION FEATURES
# ============================================================

def create_transaction_features():

    datasets = load_all_datasets()

    transactions = (
        datasets["transactions"]
        .copy()
    )

    buyers = (
        datasets["buyers"]
        .copy()
    )

    logistics = (
        datasets["logistics"]
        .copy()
    )

    print("\n" + "=" * 70)
    print("TRANSACTION / RISK FEATURE ENGINEERING")
    print("=" * 70)

    print("\nInput datasets:")

    print(
        f"Transactions : {transactions.shape}"
    )

    print(
        f"Buyers       : {buyers.shape}"
    )

    print(
        f"Logistics    : {logistics.shape}"
    )

    # ========================================================
    # REQUIRED TRANSACTION COLUMNS
    # ========================================================

    required_transaction = [
        "transaction_id",
        "farmer_id",
        "buyer_id",
        "quantity_kg",
        "agreed_price_per_kg",
        "market_price_per_kg",
        "transaction_date",
    ]

    required_buyer = [
        "buyer_id",
        "buyer_rating",
        "payment_terms_days",
        "buyer_reliability_label",
    ]

    required_logistics = [
        "transaction_id",
        "distance_km",
        "estimated_travel_hours",
        "weather_risk",
        "route_risk",
        "delivery_urgency",
    ]

    missing_transaction = [
        column
        for column in required_transaction
        if column not in transactions.columns
    ]

    missing_buyer = [
        column
        for column in required_buyer
        if column not in buyers.columns
    ]

    missing_logistics = [
        column
        for column in required_logistics
        if column not in logistics.columns
    ]

    if missing_transaction:
        raise ValueError(
            "Missing transaction columns:\n"
            f"{missing_transaction}"
        )

    if missing_buyer:
        raise ValueError(
            "Missing buyer columns:\n"
            f"{missing_buyer}"
        )

    if missing_logistics:
        raise ValueError(
            "Missing logistics columns:\n"
            f"{missing_logistics}"
        )

    # ========================================================
    # SELECT COLUMNS
    # ========================================================

    transactions = transactions[
        [
            "transaction_id",
            "farmer_id",
            "buyer_id",
            "quantity_kg",
            "agreed_price_per_kg",
            "market_price_per_kg",
            "transaction_date",
        ]
    ].copy()

    buyers = buyers[
        required_buyer
    ].copy()

    logistics = logistics[
        required_logistics
    ].copy()

    # ========================================================
    # NUMERIC CONVERSION
    # ========================================================

    transaction_numeric = [
        "quantity_kg",
        "agreed_price_per_kg",
        "market_price_per_kg",
    ]

    buyer_numeric = [
        "buyer_rating",
        "payment_terms_days",
    ]

    logistics_numeric = [
        "distance_km",
        "estimated_travel_hours",
    ]

    for column in transaction_numeric:
        transactions[column] = pd.to_numeric(
            transactions[column],
            errors="coerce"
        )

    for column in buyer_numeric:
        buyers[column] = pd.to_numeric(
            buyers[column],
            errors="coerce"
        )

    for column in logistics_numeric:
        logistics[column] = pd.to_numeric(
            logistics[column],
            errors="coerce"
        )

    # ========================================================
    # MERGE BUYER INFORMATION
    # ========================================================

    transaction_df = transactions.merge(
        buyers,
        on="buyer_id",
        how="left",
        validate="many_to_one"
    )

    print(
        f"\nAfter buyer merge: "
        f"{transaction_df.shape}"
    )

    # ========================================================
    # MERGE LOGISTICS INFORMATION
    # ========================================================

    transaction_df = transaction_df.merge(
        logistics,
        on="transaction_id",
        how="left",
        validate="one_to_one"
    )

    print(
        f"After logistics merge: "
        f"{transaction_df.shape}"
    )

    # ========================================================
    # BASIC FEATURE ENGINEERING
    # ========================================================

    transaction_df[
        "price_difference"
    ] = (
        transaction_df[
            "agreed_price_per_kg"
        ]
        -
        transaction_df[
            "market_price_per_kg"
        ]
    )

    transaction_df[
        "price_difference_percentage"
    ] = np.where(
        transaction_df[
            "market_price_per_kg"
        ] != 0,

        (
            transaction_df[
                "price_difference"
            ]
            /
            transaction_df[
                "market_price_per_kg"
            ]
        ) * 100,

        0.0
    )

    transaction_df[
        "buyer_rating_normalized"
    ] = normalize_rating(
        transaction_df[
            "buyer_rating"
        ]
    )

    transaction_df[
        "weather_risk_score"
    ] = risk_to_numeric(
        transaction_df[
            "weather_risk"
        ]
    )

    transaction_df[
        "route_risk_score"
    ] = risk_to_numeric(
        transaction_df[
            "route_risk"
        ]
    )

    transaction_df[
        "delivery_urgency_score"
    ] = urgency_to_numeric(
        transaction_df[
            "delivery_urgency"
        ]
    )

    # ========================================================
    # PAYMENT RISK SIGNAL
    # ========================================================

    # Low buyer rating increases payment risk.
    buyer_risk_component = (
        1.0
        -
        transaction_df[
            "buyer_rating_normalized"
        ]
    )

    # Extreme price deviations increase payment risk.
    price_risk_component = np.clip(
        transaction_df[
            "price_difference_percentage"
        ].abs()
        / 30.0,
        0.0,
        1.0
    )

    # Certain buyer reliability classes increase risk.
    reliability_risk = (
        transaction_df[
            "buyer_reliability_label"
        ]
        .astype("string")
        .str.upper()
        .map({
            "RELIABLE": 0.05,
            "MODERATE": 0.40,
            "UNRELIABLE": 0.90
        })
        .fillna(0.35)
    )

    payment_risk_score = (
        0.45 * reliability_risk
        + 0.35 * buyer_risk_component
        + 0.20 * price_risk_component
    )

    # Small controlled noise.
    rng = np.random.default_rng(
        RANDOM_SEED
    )

    payment_risk_score = (
        payment_risk_score
        +
        rng.normal(
            0,
            0.025,
            len(transaction_df)
        )
    )

    payment_risk_score = np.clip(
        payment_risk_score,
        0.0,
        1.0
    )

    transaction_df[
        "payment_risk_score"
    ] = payment_risk_score

    # ========================================================
    # PAYMENT STATUS TARGET
    # ========================================================

    transaction_df[
        "payment_status"
    ] = np.select(
        [
            payment_risk_score >= 0.67,
            payment_risk_score >= 0.37
        ],
        [
            "Late",
            "Pending"
        ],
        default="Paid"
    )

    # ========================================================
    # DELIVERY RISK SIGNAL
    # ========================================================

    distance_component = np.clip(
        transaction_df[
            "distance_km"
        ]
        / 300.0,
        0.0,
        1.0
    )

    travel_component = np.clip(
        transaction_df[
            "estimated_travel_hours"
        ]
        / 20.0,
        0.0,
        1.0
    )

    weather_component = (
        transaction_df[
            "weather_risk_score"
        ]
        / 2.0
    )

    route_component = (
        transaction_df[
            "route_risk_score"
        ]
        / 2.0
    )

    urgency_component = np.clip(
        transaction_df[
            "delivery_urgency_score"
        ]
        / 3.0,
        0.0,
        1.0
    )

    delivery_risk_score = (
        0.25 * distance_component
        + 0.20 * travel_component
        + 0.25 * weather_component
        + 0.20 * route_component
        + 0.10 * urgency_component
    )

    delivery_risk_score = (
        delivery_risk_score
        +
        rng.normal(
            0,
            0.025,
            len(transaction_df)
        )
    )

    delivery_risk_score = np.clip(
        delivery_risk_score,
        0.0,
        1.0
    )

    transaction_df[
        "delivery_risk_score"
    ] = delivery_risk_score

    # ========================================================
    # DELIVERY STATUS TARGET
    # ========================================================

    transaction_df[
        "delivery_status"
    ] = np.select(
        [
            delivery_risk_score >= 0.72,
            delivery_risk_score >= 0.44
        ],
        [
            "Cancelled",
            "Delayed"
        ],
        default="Delivered"
    )

    # ========================================================
    # DATETIME FEATURES
    # ========================================================

    transaction_df[
        "transaction_date"
    ] = pd.to_datetime(
        transaction_df[
            "transaction_date"
        ],
        errors="coerce"
    )

    transaction_df["transaction_month"] = (
        transaction_df[
            "transaction_date"
        ]
        .dt.month
        .fillna(0)
        .astype(int)
    )

    transaction_df["transaction_day_of_week"] = (
        transaction_df[
            "transaction_date"
        ]
        .dt.dayofweek
        .fillna(0)
        .astype(int)
    )

    transaction_df["is_weekend"] = (
        transaction_df[
            "transaction_day_of_week"
        ] >= 5
    ).astype(int)

    # ========================================================
    # CLEAN CATEGORICAL FEATURES
    # ========================================================

    transaction_df[
        "crop"
    ] = (
        transaction_df
        .get(
            "crop",
            pd.Series(
                ["UNKNOWN"] * len(transaction_df)
            )
        )
        .astype("string")
        .fillna("UNKNOWN")
        .str.strip()
    )

    for column in [
        "weather_risk",
        "route_risk",
        "delivery_urgency"
    ]:

        transaction_df[column] = (
            transaction_df[column]
            .astype("string")
            .fillna("UNKNOWN")
            .str.strip()
        )

    # ========================================================
    # NUMERICAL FEATURES FOR ML
    # ========================================================

    numerical_features = [
        "quantity_kg",
        "agreed_price_per_kg",
        "market_price_per_kg",
        "price_difference",
        "price_difference_percentage",
        "buyer_rating",
        "payment_terms_days",
        "buyer_rating_normalized",
        "weather_risk_score",
        "route_risk_score",
        "delivery_urgency_score",
        "distance_km",
        "estimated_travel_hours",
        "payment_risk_score",
        "delivery_risk_score",
        "transaction_month",
        "transaction_day_of_week",
        "is_weekend",
    ]

    # ========================================================
    # CATEGORICAL FEATURES FOR ML
    # ========================================================

    categorical_features = [
        "crop",
        "weather_risk",
        "route_risk",
        "delivery_urgency",
        "buyer_reliability_label",
    ]

    # ========================================================
    # CLEAN NUMERICAL VALUES
    # ========================================================

    transaction_df = transaction_df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    transaction_df[
        numerical_features
    ] = (
        transaction_df[
            numerical_features
        ]
        .fillna(0)
    )

    transaction_df[
        categorical_features
    ] = (
        transaction_df[
            categorical_features
        ]
        .fillna("UNKNOWN")
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    invalid_values = (
        transaction_df[
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

    missing_targets = (
        transaction_df[
            [
                "payment_status",
                "delivery_status"
            ]
        ]
        .isna()
        .sum()
        .sum()
    )

    print(
        f"\nInvalid numerical values: "
        f"{invalid_values:,}"
    )

    print(
        f"Missing target values: "
        f"{missing_targets:,}"
    )

    if invalid_values > 0:
        raise ValueError(
            "Invalid numerical feature values found."
        )

    if missing_targets > 0:
        raise ValueError(
            "Missing risk targets found."
        )

    # ========================================================
    # TARGET DISTRIBUTIONS
    # ========================================================

    print("\n" + "=" * 70)
    print("NEW PAYMENT STATUS DISTRIBUTION")
    print("=" * 70)

    print(
        transaction_df[
            "payment_status"
        ]
        .value_counts()
        .to_string()
    )

    print("\n" + "=" * 70)
    print("NEW DELIVERY STATUS DISTRIBUTION")
    print("=" * 70)

    print(
        transaction_df[
            "delivery_status"
        ]
        .value_counts()
        .to_string()
    )

    # ========================================================
    # CORRELATION CHECK
    # ========================================================

    print("\n" + "=" * 70)
    print("RISK SIGNAL CHECK")
    print("=" * 70)

    correlation_columns = [
        "buyer_rating",
        "price_difference_percentage",
        "payment_risk_score",
        "distance_km",
        "estimated_travel_hours",
        "weather_risk_score",
        "route_risk_score",
        "delivery_risk_score",
    ]

    # Binary diagnostic indicators.
    transaction_df[
        "_is_payment_risk"
    ] = transaction_df[
        "payment_status"
    ].isin(
        ["Pending", "Late"]
    ).astype(int)

    transaction_df[
        "_is_delivery_risk"
    ] = transaction_df[
        "delivery_status"
    ].isin(
        ["Delayed", "Cancelled"]
    ).astype(int)

    print("\nPayment risk correlations:")

    payment_corr = (
        transaction_df[
            correlation_columns
            + ["_is_payment_risk"]
        ]
        .corr(numeric_only=True)
        [
            "_is_payment_risk"
        ]
        .drop("_is_payment_risk")
        .sort_values(
            key=lambda x: abs(x),
            ascending=False
        )
    )

    for feature, value in payment_corr.items():

        print(
            f"{feature:35s}"
            f"{value: .4f}"
        )

    print("\nDelivery risk correlations:")

    delivery_corr = (
        transaction_df[
            correlation_columns
            + ["_is_delivery_risk"]
        ]
        .corr(numeric_only=True)
        [
            "_is_delivery_risk"
        ]
        .drop("_is_delivery_risk")
        .sort_values(
            key=lambda x: abs(x),
            ascending=False
        )
    )

    for feature, value in delivery_corr.items():

        print(
            f"{feature:35s}"
            f"{value: .4f}"
        )

    # ========================================================
    # REMOVE INTERNAL DIAGNOSTIC COLUMNS
    # ========================================================

    transaction_df = transaction_df.drop(
        columns=[
            "_is_payment_risk",
            "_is_delivery_risk"
        ]
    )

    # ========================================================
    # EXCLUDED COLUMNS
    # ========================================================

    excluded_columns = [
        "transaction_id",
        "farmer_id",
        "buyer_id",
        "buyer_reliability_label",
        "transaction_date",
        "payment_status",
        "delivery_status",
    ]

    print(
        "\nExcluded from ML features:"
    )

    print("-" * 70)

    for column in excluded_columns:

        if column in transaction_df.columns:
            print(
                f"  - {column}"
            )

    # ========================================================
    # FINAL FEATURE LIST
    # ========================================================

    feature_columns = (
        numerical_features
        + categorical_features
    )

    print(
        f"\nFinal feature count: "
        f"{len(feature_columns)}"
    )

    print(
        f"Final dataset shape: "
        f"{transaction_df.shape}"
    )

    print("\n" + "=" * 70)
    print("TRANSACTION / RISK FEATURE ENGINEERING COMPLETED")
    print("=" * 70)

    return (
        transaction_df,
        feature_columns,
        [
            "payment_status",
            "delivery_status"
        ]
    )


# ============================================================
# SAVE
# ============================================================

def save_transaction_features(
    transaction_df,
    feature_columns,
    target_columns
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    transaction_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n" + "=" * 70)
    print("TRANSACTION FEATURE DATASET SAVED")
    print("=" * 70)

    print("\nSaved to:")
    print(OUTPUT_FILE)

    print(
        f"Rows    : {len(transaction_df):,}"
    )

    print(
        f"Columns : {len(transaction_df.columns)}"
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
            transaction_df,
            feature_columns,
            target_columns
        ) = create_transaction_features()

        save_transaction_features(
            transaction_df,
            feature_columns,
            target_columns
        )

        print(
            "\n✓ Transaction / risk feature engineering "
            "completed successfully."
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("TRANSACTION / RISK FEATURE ENGINEERING FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        sys.exit(1)