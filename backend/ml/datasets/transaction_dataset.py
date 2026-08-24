"""
Transaction / Risk ML Dataset Preparation

Separate classification targets:
    1. payment_status
    2. delivery_status

Targets are NEVER mixed.
"""

import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "transaction_features.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42
TEST_SIZE = 0.20


# ============================================================
# TARGET COLUMNS
# ============================================================

TARGET_COLUMNS = [
    "payment_status",
    "delivery_status"
]


# ============================================================
# EXCLUDED COLUMNS
# ============================================================

EXCLUDED_COLUMNS = [
    "transaction_id",
    "farmer_id",
    "buyer_id",
    "total_value",
    "payment_status",
    "delivery_status",
    "delivered_quantity_kg",
    "buyer_rating",
    "transport_cost",
    "damage_quantity_kg",
    "transaction_date"
]


# ============================================================
# LOAD DATASET
# ============================================================

def load_transaction_dataset():

    print("=" * 70)
    print("TRANSACTION / RISK ML DATASET")
    print("=" * 70)

    print("\nDataset path:")
    print(DATASET_PATH)

    if not DATASET_PATH.exists():

        raise FileNotFoundError(
            f"\nTransaction feature dataset not found:\n"
            f"{DATASET_PATH}\n\n"
            f"Run transaction_features.py first."
        )

    df = pd.read_csv(DATASET_PATH)

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

def validate_transaction_dataset(df):

    print("\n" + "=" * 70)
    print("TRANSACTION DATASET VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Check targets
    # --------------------------------------------------------

    missing_target_columns = [
        target
        for target in TARGET_COLUMNS
        if target not in df.columns
    ]

    if missing_target_columns:

        raise ValueError(
            "Missing target columns: "
            f"{missing_target_columns}"
        )

    # --------------------------------------------------------
    # Target missing values
    # --------------------------------------------------------

    print("\nTarget missing values:")

    for target in TARGET_COLUMNS:

        missing = (
            df[target]
            .isna()
            .sum()
        )

        print(
            f"  {target}: {missing}"
        )

    missing_target_rows = (
        df[TARGET_COLUMNS]
        .isna()
        .any(axis=1)
        .sum()
    )

    print(
        f"\nRows with one or more "
        f"missing targets: "
        f"{missing_target_rows}"
    )

    if missing_target_rows > 0:

        df = (
            df
            .dropna(
                subset=TARGET_COLUMNS
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

    return df


# ============================================================
# PREPARE FEATURES
# ============================================================

def prepare_features(df):

    print("\n" + "=" * 70)
    print("PREPARING TRANSACTION ML FEATURES")
    print("=" * 70)

    # --------------------------------------------------------
    # Determine actual feature columns
    # --------------------------------------------------------

    feature_columns = [
        column
        for column in df.columns
        if column not in EXCLUDED_COLUMNS
    ]

    X = df[
        feature_columns
    ].copy()

    print(
        f"\nX shape: "
        f"{X.shape}"
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
        f"{len(feature_columns)}"
    )

    # ========================================================
    # NUMERICAL VALIDATION
    # ========================================================

    if numerical_columns:

        invalid_values = (
            X[numerical_columns]
            .replace(
                [float("inf"), float("-inf")],
                pd.NA
            )
            .isna()
            .sum()
            .sum()
        )

    else:

        invalid_values = 0

    print(
        f"\nInvalid numerical "
        f"feature values: "
        f"{invalid_values}"
    )

    if invalid_values > 0:

        raise ValueError(
            "Invalid numerical values "
            "found in transaction features."
        )

    # ========================================================
    # CATEGORICAL VALIDATION
    # ========================================================

    if categorical_columns:

        missing_categorical = (
            X[categorical_columns]
            .isna()
            .sum()
            .sum()
        )

    else:

        missing_categorical = 0

    print(
        f"Missing categorical "
        f"feature values: "
        f"{missing_categorical}"
    )

    if missing_categorical > 0:

        raise ValueError(
            "Missing categorical values "
            "found in transaction features."
        )

    # ========================================================
    # EXCLUDED COLUMNS
    # ========================================================

    print("\nExcluded from ML features:")

    for column in EXCLUDED_COLUMNS:

        if column in df.columns:

            print(
                f"  - {column}"
            )

    return (
        X,
        feature_columns,
        numerical_columns,
        categorical_columns
    )


# ============================================================
# PREPARE TARGETS
# ============================================================

def prepare_targets(df):

    print("\n" + "=" * 70)
    print("PREPARING TRANSACTION TARGETS")
    print("=" * 70)

    targets = {}

    for target in TARGET_COLUMNS:

        y = (
            df[target]
            .astype(str)
            .str.strip()
        )

        targets[target] = y

        print(
            f"\n{target}:"
        )

        print(
            y.value_counts()
            .to_string()
        )

    return targets


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

def split_dataset(X, targets):

    print("\n" + "=" * 70)
    print("TRAIN / TEST SPLIT")
    print("=" * 70)

    indices = list(
        range(len(X))
    )

    train_indices, test_indices = (
        train_test_split(
            indices,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE
        )
    )

    X_train = (
        X.iloc[
            train_indices
        ]
        .reset_index(drop=True)
    )

    X_test = (
        X.iloc[
            test_indices
        ]
        .reset_index(drop=True)
    )

    target_splits = {}

    for target_name, y in targets.items():

        y_train = (
            y.iloc[
                train_indices
            ]
            .reset_index(drop=True)
        )

        y_test = (
            y.iloc[
                test_indices
            ]
            .reset_index(drop=True)
        )

        target_splits[target_name] = {
            "y_train": y_train,
            "y_test": y_test
        }

    print("\nTraining:")

    print(
        f"  X_train: "
        f"{X_train.shape}"
    )

    print("\nTesting:")

    print(
        f"  X_test : "
        f"{X_test.shape}"
    )

    print("\nTarget splits:")

    for target_name, split in target_splits.items():

        print(
            f"  {target_name}: "
            f"train={split['y_train'].shape}, "
            f"test={split['y_test'].shape}"
        )

    # --------------------------------------------------------
    # Target distributions
    # --------------------------------------------------------

    print("\nTraining target distributions:")

    for target_name, split in target_splits.items():

        print(
            f"\n{target_name}:"
        )

        print(
            split["y_train"]
            .value_counts()
            .to_string()
        )

    print("\nTesting target distributions:")

    for target_name, split in target_splits.items():

        print(
            f"\n{target_name}:"
        )

        print(
            split["y_test"]
            .value_counts()
            .to_string()
        )

    return (
        X_train,
        X_test,
        target_splits
    )


# ============================================================
# COMPLETE DATASET PREPARATION
# ============================================================

def prepare_transaction_dataset():

    # --------------------------------------------------------
    # 1. Load
    # --------------------------------------------------------

    df = load_transaction_dataset()

    # --------------------------------------------------------
    # 2. Validate
    # --------------------------------------------------------

    df = validate_transaction_dataset(df)

    # --------------------------------------------------------
    # 3. Prepare features
    # --------------------------------------------------------

    (
        X,
        feature_columns,
        numerical_columns,
        categorical_columns
    ) = prepare_features(df)

    # --------------------------------------------------------
    # 4. Prepare targets
    # --------------------------------------------------------

    targets = prepare_targets(df)

    # --------------------------------------------------------
    # 5. Split
    # --------------------------------------------------------

    (
        X_train,
        X_test,
        target_splits
    ) = split_dataset(
        X,
        targets
    )

    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    print("\n" + "=" * 70)
    print("TRANSACTION ML DATASET READY")
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

    print("\nSeparate classification targets:")

    for target in TARGET_COLUMNS:

        print(
            f"  - {target}"
        )

    print("\n" + "=" * 70)

    return {
        "df": df,
        "X": X,
        "X_train": X_train,
        "X_test": X_test,
        "targets": targets,
        "target_splits": target_splits,
        "feature_columns": feature_columns,
        "numerical_columns": numerical_columns,
        "categorical_columns": categorical_columns
    }


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    try:

        dataset = (
            prepare_transaction_dataset()
        )

        print(
            "\n✓ Transaction dataset preparation "
            "completed successfully."
        )

        print(
            "✓ Ready for the transaction/risk models."
        )

    except Exception as e:

        print("\n" + "=" * 70)
        print("TRANSACTION DATASET PREPARATION FAILED")
        print("=" * 70)

        print(
            f"\nError: {e}"
        )

        sys.exit(1)