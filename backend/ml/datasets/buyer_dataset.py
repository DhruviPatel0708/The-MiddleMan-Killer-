"""
Buyer Reliability ML Dataset Preparation

Source:
    data/raw/buyers.csv
    -> processed by buyer_features.py
    -> data/processed/buyer_features.csv

Target:
    buyer_reliability_label

Problem:
    Multiclass classification

Expected synthetic distribution:
    RELIABLE      1750
    MODERATE       500
    UNRELIABLE     250
"""

import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# DATASET PATH
# ============================================================

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "buyer_features.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42
TEST_SIZE = 0.20

TARGET_COLUMN = "buyer_reliability_label"


# ============================================================
# EXPECTED FEATURES
# ============================================================

NUMERICAL_FEATURES = [
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
    "successful_transaction_rate",
    "cancellation_rate",
    "late_payment_rate",
    "successful_transactions_per_total",
    "acceptable_quantity_range_kg",
    "required_quantity_to_max_ratio",
    "payment_delay_to_terms_ratio",
]


CATEGORICAL_FEATURES = [
    "buyer_type",
    "district",
    "market",
    "preferred_crop",
    "minimum_quality_grade",
    "storage_available",
]


# ============================================================
# LOAD DATASET
# ============================================================

def load_buyer_dataset():

    print("=" * 70)
    print("BUYER RELIABILITY ML DATASET")
    print("=" * 70)

    print("\nDataset path:")
    print(DATASET_PATH)

    if not DATASET_PATH.exists():

        raise FileNotFoundError(
            f"\nBuyer feature dataset not found:\n"
            f"{DATASET_PATH}\n\n"
            f"Run buyer_features.py first."
        )

    df = pd.read_csv(
        DATASET_PATH
    )

    print("\nDataset loaded successfully.")

    print(
        f"Rows    : "
        f"{len(df):,}"
    )

    print(
        f"Columns : "
        f"{len(df.columns)}"
    )

    return df


# ============================================================
# VALIDATE DATASET
# ============================================================

def validate_buyer_dataset(df):

    print("\n" + "=" * 70)
    print("BUYER DATASET VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Target check
    # --------------------------------------------------------

    if TARGET_COLUMN not in df.columns:

        raise ValueError(
            f"Target column not found: "
            f"{TARGET_COLUMN}"
        )

    # --------------------------------------------------------
    # Missing target
    # --------------------------------------------------------

    missing_target = (
        df[TARGET_COLUMN]
        .isna()
        .sum()
    )

    print(
        f"\nTarget column : "
        f"{TARGET_COLUMN}"
    )

    print(
        f"Missing target: "
        f"{missing_target}"
    )

    if missing_target > 0:

        df = (
            df
            .dropna(
                subset=[TARGET_COLUMN]
            )
            .reset_index(drop=True)
        )

    # --------------------------------------------------------
    # Duplicate rows
    # --------------------------------------------------------

    duplicate_rows = (
        df
        .duplicated()
        .sum()
    )

    print(
        f"Duplicate rows : "
        f"{duplicate_rows}"
    )

    if duplicate_rows > 0:

        df = (
            df
            .drop_duplicates()
            .reset_index(drop=True)
        )

    print(
        f"\nFinal dataset shape: "
        f"{df.shape}"
    )

    # --------------------------------------------------------
    # Target distribution
    # --------------------------------------------------------

    print("\nTarget distribution:")
    print("-" * 70)

    print(
        df[TARGET_COLUMN]
        .value_counts()
        .to_string()
    )

    # --------------------------------------------------------
    # Check expected classes
    # --------------------------------------------------------

    expected_classes = {
        "RELIABLE",
        "MODERATE",
        "UNRELIABLE"
    }

    actual_classes = set(
        df[TARGET_COLUMN]
        .astype(str)
        .str.strip()
        .unique()
    )

    missing_classes = (
        expected_classes
        - actual_classes
    )

    if missing_classes:

        raise ValueError(
            "Missing buyer reliability classes: "
            f"{sorted(missing_classes)}"
        )

    return df


# ============================================================
# PREPARE X AND y
# ============================================================

def prepare_features_and_target(df):

    print("\n" + "=" * 70)
    print("PREPARING X AND y")
    print("=" * 70)

    # --------------------------------------------------------
    # Verify all expected feature columns
    # --------------------------------------------------------

    expected_features = (
        NUMERICAL_FEATURES
        + CATEGORICAL_FEATURES
    )

    missing_features = [
        column
        for column in expected_features
        if column not in df.columns
    ]

    if missing_features:

        raise ValueError(
            "Missing expected buyer feature columns:\n"
            f"{missing_features}"
        )

    # --------------------------------------------------------
    # X
    # --------------------------------------------------------

    X = df[
        expected_features
    ].copy()

    # --------------------------------------------------------
    # y
    # --------------------------------------------------------

    y = (
        df[TARGET_COLUMN]
        .astype(str)
        .str.strip()
        .copy()
    )

    print(
        f"\nX shape: "
        f"{X.shape}"
    )

    print(
        f"y shape: "
        f"{y.shape}"
    )

    # ========================================================
    # NUMERICAL FEATURES
    # ========================================================

    print("\nNumerical features:")

    for column in NUMERICAL_FEATURES:

        print(
            f"  - {column}"
        )

    # ========================================================
    # CATEGORICAL FEATURES
    # ========================================================

    print("\nCategorical features:")

    for column in CATEGORICAL_FEATURES:

        print(
            f"  - {column}"
        )

    print(
        f"\nTotal ML features: "
        f"{len(expected_features)}"
    )

    # ========================================================
    # NUMERICAL VALIDATION
    # ========================================================

    numerical_values = (
        X[
            NUMERICAL_FEATURES
        ]
        .apply(
            pd.to_numeric,
            errors="coerce"
        )
        .replace(
            [float("inf"), float("-inf")],
            pd.NA
        )
    )

    invalid_numerical_values = (
        numerical_values
        .isna()
        .sum()
        .sum()
    )

    print(
        f"\nInvalid numerical feature values: "
        f"{invalid_numerical_values}"
    )

    if invalid_numerical_values > 0:

        raise ValueError(
            "Invalid numerical values found "
            "in buyer features."
        )

    # ========================================================
    # CATEGORICAL VALIDATION
    # ========================================================

    missing_categorical_values = (
        X[
            CATEGORICAL_FEATURES
        ]
        .isna()
        .sum()
        .sum()
    )

    print(
        f"Missing categorical feature values: "
        f"{missing_categorical_values}"
    )

    if missing_categorical_values > 0:

        raise ValueError(
            "Missing categorical values found "
            "in buyer features."
        )

    # ========================================================
    # TARGET TYPE
    # ========================================================

    if not pd.api.types.is_string_dtype(y):

        y = y.astype(str)

    # ========================================================
    # EXCLUDED COLUMNS
    # ========================================================

    print("\nExcluded from ML features:")
    print("-" * 70)

    excluded_columns = [
        "buyer_id",
        "buyer_name",
        "reliability_score",
        "buyer_reliability_label"
    ]

    for column in excluded_columns:

        if column in df.columns:

            print(
                f"  - {column}"
            )

    return (
        X,
        y
    )


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

def split_dataset(X, y):

    print("\n" + "=" * 70)
    print("STRATIFIED TRAIN / TEST SPLIT")
    print("=" * 70)

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            stratify=y
        )
    )

    # --------------------------------------------------------
    # Reset indices
    # --------------------------------------------------------

    X_train = (
        X_train
        .reset_index(drop=True)
    )

    X_test = (
        X_test
        .reset_index(drop=True)
    )

    y_train = (
        y_train
        .reset_index(drop=True)
    )

    y_test = (
        y_test
        .reset_index(drop=True)
    )

    # ========================================================
    # SHAPES
    # ========================================================

    print("\nSplit completed.")

    print("\nTraining:")

    print(
        f"  X_train: "
        f"{X_train.shape}"
    )

    print(
        f"  y_train: "
        f"{y_train.shape}"
    )

    print("\nTesting:")

    print(
        f"  X_test : "
        f"{X_test.shape}"
    )

    print(
        f"  y_test : "
        f"{y_test.shape}"
    )

    # ========================================================
    # TRAINING DISTRIBUTION
    # ========================================================

    print("\nTraining target distribution:")

    print(
        y_train
        .value_counts()
        .to_string()
    )

    # ========================================================
    # TEST DISTRIBUTION
    # ========================================================

    print("\nTesting target distribution:")

    print(
        y_test
        .value_counts()
        .to_string()
    )

    return (
        X_train,
        X_test,
        y_train,
        y_test
    )


# ============================================================
# COMPLETE PREPARATION
# ============================================================

def prepare_buyer_dataset():

    # --------------------------------------------------------
    # 1. Load
    # --------------------------------------------------------

    df = load_buyer_dataset()

    # --------------------------------------------------------
    # 2. Validate
    # --------------------------------------------------------

    df = validate_buyer_dataset(
        df
    )

    # --------------------------------------------------------
    # 3. Prepare X and y
    # --------------------------------------------------------

    X, y = (
        prepare_features_and_target(
            df
        )
    )

    # --------------------------------------------------------
    # 4. Split
    # --------------------------------------------------------

    (
        X_train,
        X_test,
        y_train,
        y_test
    ) = split_dataset(
        X,
        y
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("BUYER ML DATASET READY")
    print("=" * 70)

    print(
        f"\nTotal rows : "
        f"{len(df):,}"
    )

    print(
        f"Features   : "
        f"{X.shape[1]}"
    )

    print(
        f"Train rows : "
        f"{len(X_train):,}"
    )

    print(
        f"Test rows  : "
        f"{len(X_test):,}"
    )

    print(
        "\nFinal target distribution:"
    )

    print(
        y.value_counts()
        .to_string()
    )

    print("\n" + "=" * 70)

    return {
        "df": df,
        "X": X,
        "y": y,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "numerical_columns": NUMERICAL_FEATURES,
        "categorical_columns": CATEGORICAL_FEATURES,
    }


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    try:

        dataset = (
            prepare_buyer_dataset()
        )

        print(
            "\n✓ Buyer dataset preparation "
            "completed successfully."
        )

        print(
            "✓ Ready for the buyer reliability model."
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("BUYER DATASET PREPARATION FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        sys.exit(1)