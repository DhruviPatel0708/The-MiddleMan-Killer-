"""
Cost Estimation ML Dataset Preparation

Source:
    data/processed/cost_features.csv

Target:
    estimated_total_cost

Problem:
    Regression
"""

import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


# ============================================================
# PROJECT ROOT
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
    / "cost_features.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42
TEST_SIZE = 0.20

TARGET_COLUMN = "estimated_total_cost"


# ============================================================
# FEATURES
# ============================================================

NUMERICAL_FEATURES = [
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


CATEGORICAL_FEATURES = [
    "district",
    "market",
    "crop",
    "vehicle_type",
    "weather_risk",
    "route_risk",
    "delivery_urgency",
]


ALL_FEATURES = (
    NUMERICAL_FEATURES
    + CATEGORICAL_FEATURES
)


# ============================================================
# LOAD DATASET
# ============================================================

def load_cost_dataset():

    print("=" * 70)
    print("COST ESTIMATION ML DATASET")
    print("=" * 70)

    print("\nDataset path:")
    print(DATASET_PATH)

    if not DATASET_PATH.exists():

        raise FileNotFoundError(
            f"\nCost feature dataset not found:\n"
            f"{DATASET_PATH}\n\n"
            f"Run cost_features.py first."
        )

    df = pd.read_csv(
        DATASET_PATH
    )

    print("\nDataset loaded successfully.")

    print(
        f"Rows    : {len(df):,}"
    )

    print(
        f"Columns : {len(df.columns)}"
    )

    return df


# ============================================================
# VALIDATE DATASET
# ============================================================

def validate_cost_dataset(df):

    print("\n" + "=" * 70)
    print("COST DATASET VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Target
    # --------------------------------------------------------

    if TARGET_COLUMN not in df.columns:

        raise ValueError(
            f"Target column not found: "
            f"{TARGET_COLUMN}"
        )

    missing_target = (
        df[TARGET_COLUMN]
        .isna()
        .sum()
    )

    duplicate_rows = (
        df.duplicated()
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

    print(
        f"Duplicate rows : "
        f"{duplicate_rows}"
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
    # Check expected features
    # --------------------------------------------------------

    missing_features = [
        column
        for column in ALL_FEATURES
        if column not in df.columns
    ]

    if missing_features:

        raise ValueError(
            "Missing expected cost features:\n"
            f"{missing_features}"
        )

    print(
        f"\nFinal dataset shape: "
        f"{df.shape}"
    )

    return df


# ============================================================
# PREPARE X AND y
# ============================================================

def prepare_features_and_target(df):

    print("\n" + "=" * 70)
    print("PREPARING COST ML FEATURES")
    print("=" * 70)

    X = df[
        ALL_FEATURES
    ].copy()

    y = df[
        TARGET_COLUMN
    ].copy()

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
        f"{len(ALL_FEATURES)}"
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
            "in cost features."
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
            "in cost features."
        )

    # ========================================================
    # TARGET VALIDATION
    # ========================================================

    y = pd.to_numeric(
        y,
        errors="coerce"
    )

    invalid_target = (
        y.isna()
        .sum()
    )

    print(
        f"Invalid target values: "
        f"{invalid_target}"
    )

    if invalid_target > 0:

        raise ValueError(
            "Invalid values found in "
            "estimated_total_cost."
        )

    return X, y


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

def split_cost_dataset(X, y):

    print("\n" + "=" * 70)
    print("TRAIN / TEST SPLIT")
    print("=" * 70)

    (
        X_train,
        X_test,
        y_train,
        y_test
    ) = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE
    )

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

    print("\nTraining:")

    print(
        f"X_train: "
        f"{X_train.shape}"
    )

    print(
        f"y_train: "
        f"{y_train.shape}"
    )

    print("\nTesting:")

    print(
        f"X_test : "
        f"{X_test.shape}"
    )

    print(
        f"y_test : "
        f"{y_test.shape}"
    )

    # ========================================================
    # TARGET STATISTICS
    # ========================================================

    print("\nTarget statistics:")

    print(
        f"Minimum : "
        f"{y.min():.2f}"
    )

    print(
        f"Maximum : "
        f"{y.max():.2f}"
    )

    print(
        f"Mean    : "
        f"{y.mean():.2f}"
    )

    print(
        f"Median  : "
        f"{y.median():.2f}"
    )

    print(
        f"Std     : "
        f"{y.std():.2f}"
    )

    return (
        X_train,
        X_test,
        y_train,
        y_test
    )


# ============================================================
# COMPLETE DATASET PREPARATION
# ============================================================

def prepare_cost_dataset():

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    df = load_cost_dataset()

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    df = validate_cost_dataset(
        df
    )

    # --------------------------------------------------------
    # X / y
    # --------------------------------------------------------

    X, y = (
        prepare_features_and_target(
            df
        )
    )

    # --------------------------------------------------------
    # SPLIT
    # --------------------------------------------------------

    (
        X_train,
        X_test,
        y_train,
        y_test
    ) = split_cost_dataset(
        X,
        y
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("COST ML DATASET READY")
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
        f"\nTarget:"
    )

    print(
        f"  - {TARGET_COLUMN}"
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
        "target_column": TARGET_COLUMN,
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        prepare_cost_dataset()

        print(
            "\n✓ Cost dataset preparation "
            "completed successfully."
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("COST DATASET PREPARATION FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        sys.exit(1)