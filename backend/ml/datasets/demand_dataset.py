"""
Demand Forecasting ML Dataset Preparation

Target:
    next_day_demand_tonnes

Excluded from ML features:
    demand_id
    date
    next_day_demand_tonnes
"""

import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

PROCESSED_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)


# ============================================================
# DATASET CONFIGURATION
# ============================================================

TARGET_COLUMN = "next_day_demand_tonnes"

DATASET_FILE = (
    PROCESSED_DATA_DIR
    / "demand_features.csv"
)

RANDOM_STATE = 42
TEST_SIZE = 0.20


# ============================================================
# COLUMNS EXCLUDED FROM ML FEATURES
# ============================================================

EXCLUDED_COLUMNS = [
    "demand_id",
    "date",
    TARGET_COLUMN
]


# ============================================================
# LOAD DATASET
# ============================================================

def load_demand_dataset():

    print("=" * 70)
    print("DEMAND FORECASTING ML DATASET")
    print("=" * 70)

    print("\nDataset path:")
    print(DATASET_FILE)

    if not DATASET_FILE.exists():

        raise FileNotFoundError(
            f"\nDemand feature dataset not found:\n"
            f"{DATASET_FILE}\n\n"
            f"Run demand_features.py first to generate it."
        )

    df = pd.read_csv(DATASET_FILE)

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

def validate_demand_dataset(df):

    print("\n" + "=" * 70)
    print("DEMAND DATASET VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Target existence
    # --------------------------------------------------------

    if TARGET_COLUMN not in df.columns:

        raise ValueError(
            f"Target column '{TARGET_COLUMN}' "
            f"not found."
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
        f"\nTarget column : {TARGET_COLUMN}"
    )

    print(
        f"Missing target: {missing_target}"
    )

    if missing_target > 0:

        print(
            f"\nRemoving "
            f"{missing_target:,} rows "
            f"with missing target..."
        )

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

    duplicate_rows = df.duplicated().sum()

    print(
        f"Duplicate rows : {duplicate_rows}"
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

    return df


# ============================================================
# PREPARE FEATURES AND TARGET
# ============================================================

def prepare_features_and_target(df):

    print("\n" + "=" * 70)
    print("PREPARING X AND y")
    print("=" * 70)

    # --------------------------------------------------------
    # Verify excluded columns
    # --------------------------------------------------------

    missing_excluded = [
        column
        for column in EXCLUDED_COLUMNS
        if column not in df.columns
    ]

    if missing_excluded:

        raise ValueError(
            "Expected columns missing from dataset: "
            f"{missing_excluded}"
        )

    # --------------------------------------------------------
    # Create X
    # --------------------------------------------------------

    X = df.drop(
        columns=EXCLUDED_COLUMNS
    ).copy()

    # --------------------------------------------------------
    # Create y
    # --------------------------------------------------------

    y = df[
        TARGET_COLUMN
    ].copy()

    print(
        f"\nX shape: {X.shape}"
    )

    print(
        f"y shape: {y.shape}"
    )

    # ========================================================
    # NUMERICAL FEATURES
    # ========================================================

    numerical_columns = (
        X
        .select_dtypes(
            include=["number"]
        )
        .columns
        .tolist()
    )

    print("\nNumerical features:")

    for column in numerical_columns:

        print(
            f"  - {column}"
        )

    # ========================================================
    # CATEGORICAL FEATURES
    # ========================================================

    categorical_columns = (
        X
        .select_dtypes(
            include=[
                "object",
                "string",
                "category"
            ]
        )
        .columns
        .tolist()
    )

    print("\nCategorical features:")

    for column in categorical_columns:

        print(
            f"  - {column}"
        )

    print(
        f"\nTotal ML features: "
        f"{len(X.columns)}"
    )

    # ========================================================
    # TARGET VALIDATION
    # ========================================================

    if y.isna().any():

        raise ValueError(
            "Target contains missing values."
        )

    if not pd.api.types.is_numeric_dtype(y):

        raise ValueError(
            "Demand target must be numerical."
        )

    # ========================================================
    # NUMERICAL VALUE VALIDATION
    # ========================================================

    numerical_values = (
        X[numerical_columns]
        .replace(
            [float("inf"), float("-inf")],
            pd.NA
        )
    )

    invalid_values = (
        numerical_values
        .isna()
        .sum()
        .sum()
    )

    print(
        f"\nInvalid numerical "
        f"feature values: "
        f"{invalid_values:,}"
    )

    if invalid_values != 0:

        raise ValueError(
            "Invalid numerical values "
            "found in demand features."
        )

    # ========================================================
    # TARGET LEAKAGE CHECK
    # ========================================================

    if TARGET_COLUMN in X.columns:

        raise ValueError(
            "TARGET LEAKAGE: target column "
            "is present in X."
        )

    # ========================================================
    # EXCLUDED COLUMN CHECK
    # ========================================================

    print("\nExcluded from ML features:")

    for column in EXCLUDED_COLUMNS:

        print(
            f"  - {column}"
        )

    for column in EXCLUDED_COLUMNS:

        if column in X.columns:

            raise ValueError(
                f"Excluded column '{column}' "
                f"was found in X."
            )

    return (
        X,
        y,
        numerical_columns,
        categorical_columns
    )


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

def split_dataset(X, y):

    print("\n" + "=" * 70)
    print("TRAIN / TEST SPLIT")
    print("=" * 70)

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE
        )
    )

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

    return (
        X_train,
        X_test,
        y_train,
        y_test
    )


# ============================================================
# MAIN DATASET PREPARATION
# ============================================================

def prepare_demand_dataset():

    # --------------------------------------------------------
    # 1. Load
    # --------------------------------------------------------

    df = load_demand_dataset()

    # --------------------------------------------------------
    # 2. Validate
    # --------------------------------------------------------

    df = validate_demand_dataset(df)

    # --------------------------------------------------------
    # 3. Prepare X and y
    # --------------------------------------------------------

    (
        X,
        y,
        numerical_columns,
        categorical_columns
    ) = prepare_features_and_target(df)

    # --------------------------------------------------------
    # 4. Train / test split
    # --------------------------------------------------------

    (
        X_train,
        X_test,
        y_train,
        y_test
    ) = split_dataset(X, y)

    # ========================================================
    # FINAL INFORMATION
    # ========================================================

    print("\n" + "=" * 70)
    print("DEMAND ML DATASET READY")
    print("=" * 70)

    print(
        f"\nTotal rows : {len(df):,}"
    )

    print(
        f"Features   : {X.shape[1]}"
    )

    print(
        f"Train rows : {len(X_train):,}"
    )

    print(
        f"Test rows  : {len(X_test):,}"
    )

    print("\nTarget statistics:")

    print(
        f"  Minimum : "
        f"{y.min():.2f}"
    )

    print(
        f"  Maximum : "
        f"{y.max():.2f}"
    )

    print(
        f"  Mean    : "
        f"{y.mean():.2f}"
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
        "numerical_columns": numerical_columns,
        "categorical_columns": categorical_columns
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    try:

        dataset = prepare_demand_dataset()

        print(
            "\n✓ Demand dataset preparation "
            "completed successfully."
        )

        print(
            "✓ Ready for the demand forecasting model."
        )

    except Exception as e:

        print("\n" + "=" * 70)
        print("DEMAND DATASET PREPARATION FAILED")
        print("=" * 70)

        print(
            f"\nError: {e}"
        )

        sys.exit(1)