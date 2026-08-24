"""
Logistics ML Dataset Preparation

Separate regression targets:
    transport_cost
    delay_hours
    damage_percentage

The three targets are kept separate and are NOT mixed.
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

DATASET_FILE = (
    PROCESSED_DATA_DIR
    / "logistics_features.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42
TEST_SIZE = 0.20


# ============================================================
# TARGETS
# ============================================================

TARGET_COLUMNS = [
    "transport_cost",
    "delay_hours",
    "damage_percentage"
]


# ============================================================
# IDENTIFIER COLUMNS
# ============================================================

EXCLUDED_COLUMNS = [
    "logistics_id",
    "transaction_id",
    "farmer_id",
    "buyer_id"
]


# ============================================================
# LOAD DATASET
# ============================================================

def load_logistics_dataset():

    print("=" * 70)
    print("LOGISTICS ML DATASET")
    print("=" * 70)

    print("\nDataset path:")
    print(DATASET_FILE)

    if not DATASET_FILE.exists():

        raise FileNotFoundError(
            f"\nLogistics feature dataset not found:\n"
            f"{DATASET_FILE}\n\n"
            f"Run logistics_features.py first to generate it."
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
# VALIDATION
# ============================================================

def validate_logistics_dataset(df):

    print("\n" + "=" * 70)
    print("LOGISTICS DATASET VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Check target columns
    # --------------------------------------------------------

    missing_targets = [
        target
        for target in TARGET_COLUMNS
        if target not in df.columns
    ]

    if missing_targets:

        raise ValueError(
            "Missing target columns: "
            f"{missing_targets}"
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

    total_missing = (
        df[TARGET_COLUMNS]
        .isna()
        .any(axis=1)
        .sum()
    )

    print(
        f"\nRows with one or more "
        f"missing targets: "
        f"{total_missing}"
    )

    if total_missing > 0:

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
    print("PREPARING LOGISTICS ML FEATURES")
    print("=" * 70)

    # --------------------------------------------------------
    # Verify identifier columns
    # --------------------------------------------------------

    missing_ids = [
        column
        for column in EXCLUDED_COLUMNS
        if column not in df.columns
    ]

    if missing_ids:

        raise ValueError(
            "Expected identifier columns missing: "
            f"{missing_ids}"
        )

    # --------------------------------------------------------
    # Exclude IDs + all targets
    # --------------------------------------------------------

    columns_to_exclude = (
        EXCLUDED_COLUMNS
        + TARGET_COLUMNS
    )

    X = df.drop(
        columns=columns_to_exclude
    ).copy()

    print(
        f"\nX shape: {X.shape}"
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
    # NUMERICAL VALIDATION
    # ========================================================

    if numerical_columns:

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

    else:

        invalid_values = 0

    print(
        f"\nInvalid numerical "
        f"feature values: "
        f"{invalid_values:,}"
    )

    if invalid_values != 0:

        raise ValueError(
            "Invalid numerical values "
            "found in logistics features."
        )

    # ========================================================
    # CATEGORICAL VALIDATION
    # ========================================================

    if categorical_columns:

        categorical_missing = (
            X[categorical_columns]
            .isna()
            .sum()
            .sum()
        )

    else:

        categorical_missing = 0

    print(
        f"Missing categorical "
        f"feature values: "
        f"{categorical_missing:,}"
    )

    if categorical_missing != 0:

        raise ValueError(
            "Missing values found in "
            "categorical logistics features."
        )

    # ========================================================
    # PRINT EXCLUDED COLUMNS
    # ========================================================

    print("\nExcluded from ML features:")

    for column in columns_to_exclude:

        print(
            f"  - {column}"
        )

    return (
        X,
        numerical_columns,
        categorical_columns
    )


# ============================================================
# PREPARE TARGETS
# ============================================================

def prepare_targets(df):

    print("\n" + "=" * 70)
    print("PREPARING LOGISTICS TARGETS")
    print("=" * 70)

    targets = {}

    for target in TARGET_COLUMNS:

        y = df[target].copy()

        targets[target] = y

        print(f"\n{target}:")

        print(
            f"  Minimum: "
            f"{y.min():.2f}"
        )

        print(
            f"  Maximum: "
            f"{y.max():.2f}"
        )

        print(
            f"  Mean   : "
            f"{y.mean():.2f}"
        )

    return targets


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

def split_dataset(X, targets):

    print("\n" + "=" * 70)
    print("TRAIN / TEST SPLIT")
    print("=" * 70)

    # --------------------------------------------------------
    # One common split is used for all three targets.
    # This keeps all target rows aligned.
    # --------------------------------------------------------

    indices = list(range(len(X)))

    train_indices, test_indices = (
        train_test_split(
            indices,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE
        )
    )

    X_train = X.iloc[
        train_indices
    ].copy()

    X_test = X.iloc[
        test_indices
    ].copy()

    target_splits = {}

    for target_name, y in targets.items():

        y_train = y.iloc[
            train_indices
        ].copy()

        y_test = y.iloc[
            test_indices
        ].copy()

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

    return (
        X_train,
        X_test,
        target_splits
    )


# ============================================================
# MAIN DATASET PREPARATION
# ============================================================

def prepare_logistics_dataset():

    # --------------------------------------------------------
    # 1. Load
    # --------------------------------------------------------

    df = load_logistics_dataset()

    # --------------------------------------------------------
    # 2. Validate
    # --------------------------------------------------------

    df = validate_logistics_dataset(df)

    # --------------------------------------------------------
    # 3. Prepare features
    # --------------------------------------------------------

    (
        X,
        numerical_columns,
        categorical_columns
    ) = prepare_features(df)

    # --------------------------------------------------------
    # 4. Prepare targets
    # --------------------------------------------------------

    targets = prepare_targets(df)

    # --------------------------------------------------------
    # 5. Train/test split
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
    # FINAL INFORMATION
    # ========================================================

    print("\n" + "=" * 70)
    print("LOGISTICS ML DATASET READY")
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

    print("\nSeparate regression targets:")

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
        "numerical_columns": numerical_columns,
        "categorical_columns": categorical_columns
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    try:

        dataset = prepare_logistics_dataset()

        print(
            "\n✓ Logistics dataset preparation "
            "completed successfully."
        )

        print(
            "✓ Ready for the logistics models."
        )

    except Exception as e:

        print("\n" + "=" * 70)
        print("LOGISTICS DATASET PREPARATION FAILED")
        print("=" * 70)

        print(
            f"\nError: {e}"
        )

        sys.exit(1)