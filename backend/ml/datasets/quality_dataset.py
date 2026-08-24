"""
Crop Quality ML Dataset Preparation

Targets:
    quality_score
    quality_grade
    spoilage_risk_score
    spoilage_risk

All four targets are kept separately.
They must NOT be mixed during model training.
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

DATASET_FILE = (
    PROCESSED_DATA_DIR
    / "quality_features.csv"
)

RANDOM_STATE = 42
TEST_SIZE = 0.20


# ============================================================
# TARGET COLUMNS
# ============================================================

REGRESSION_TARGETS = [
    "quality_score",
    "spoilage_risk_score"
]

CLASSIFICATION_TARGETS = [
    "quality_grade",
    "spoilage_risk"
]

ALL_TARGETS = (
    REGRESSION_TARGETS
    + CLASSIFICATION_TARGETS
)


# ============================================================
# IDENTIFIER COLUMNS
# ============================================================

EXCLUDED_COLUMNS = [
    "quality_id",
    "transaction_id",
    "farmer_id"
]


# ============================================================
# LOAD DATASET
# ============================================================

def load_quality_dataset():

    print("=" * 70)
    print("CROP QUALITY ML DATASET")
    print("=" * 70)

    print("\nDataset path:")
    print(DATASET_FILE)

    if not DATASET_FILE.exists():

        raise FileNotFoundError(
            f"\nQuality feature dataset not found:\n"
            f"{DATASET_FILE}\n\n"
            f"Run quality_features.py first."
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

def validate_quality_dataset(df):

    print("\n" + "=" * 70)
    print("QUALITY DATASET VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Check all targets
    # --------------------------------------------------------

    missing_targets = [
        target
        for target in ALL_TARGETS
        if target not in df.columns
    ]

    if missing_targets:

        raise ValueError(
            "Missing target columns: "
            f"{missing_targets}"
        )

    # --------------------------------------------------------
    # Missing target values
    # --------------------------------------------------------

    print("\nTarget missing values:")

    for target in ALL_TARGETS:

        missing = (
            df[target]
            .isna()
            .sum()
        )

        print(
            f"  {target}: {missing}"
        )

    total_missing = (
        df[ALL_TARGETS]
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
                subset=ALL_TARGETS
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
    print("PREPARING QUALITY ML FEATURES")
    print("=" * 70)

    # --------------------------------------------------------
    # Features = everything except IDs and ALL targets
    # --------------------------------------------------------

    columns_to_exclude = (
        EXCLUDED_COLUMNS
        + ALL_TARGETS
    )

    missing_excluded = [
        column
        for column in EXCLUDED_COLUMNS
        if column not in df.columns
    ]

    if missing_excluded:

        raise ValueError(
            "Expected identifier columns missing: "
            f"{missing_excluded}"
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
            "found in quality features."
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
            "categorical quality features."
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
    print("PREPARING QUALITY TARGETS")
    print("=" * 70)

    targets = {}

    # ========================================================
    # QUALITY SCORE
    # ========================================================

    y_quality_score = (
        df["quality_score"]
        .copy()
    )

    print("\nQuality Score:")
    print(
        f"  Minimum: "
        f"{y_quality_score.min():.2f}"
    )

    print(
        f"  Maximum: "
        f"{y_quality_score.max():.2f}"
    )

    print(
        f"  Mean   : "
        f"{y_quality_score.mean():.2f}"
    )

    targets[
        "quality_score"
    ] = y_quality_score

    # ========================================================
    # QUALITY GRADE
    # ========================================================

    y_quality_grade = (
        df["quality_grade"]
        .copy()
    )

    print("\nQuality Grade:")

    print(
        y_quality_grade
        .value_counts()
        .to_string()
    )

    targets[
        "quality_grade"
    ] = y_quality_grade

    # ========================================================
    # SPOILAGE RISK SCORE
    # ========================================================

    y_spoilage_score = (
        df["spoilage_risk_score"]
        .copy()
    )

    print("\nSpoilage Risk Score:")

    print(
        f"  Minimum: "
        f"{y_spoilage_score.min():.2f}"
    )

    print(
        f"  Maximum: "
        f"{y_spoilage_score.max():.2f}"
    )

    print(
        f"  Mean   : "
        f"{y_spoilage_score.mean():.2f}"
    )

    targets[
        "spoilage_risk_score"
    ] = y_spoilage_score

    # ========================================================
    # SPOILAGE RISK
    # ========================================================

    y_spoilage_risk = (
        df["spoilage_risk"]
        .copy()
    )

    print("\nSpoilage Risk:")

    print(
        y_spoilage_risk
        .value_counts()
        .to_string()
    )

    targets[
        "spoilage_risk"
    ] = y_spoilage_risk

    return targets


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

def split_dataset(X, targets):

    print("\n" + "=" * 70)
    print("TRAIN / TEST SPLIT")
    print("=" * 70)

    # --------------------------------------------------------
    # Use one common split for all four targets.
    # This keeps every target aligned with the same samples.
    # --------------------------------------------------------

    indices = range(len(X))

    train_indices, test_indices = (
        train_test_split(
            list(indices),
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

    # --------------------------------------------------------
    # Target shapes
    # --------------------------------------------------------

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

def prepare_quality_dataset():

    # --------------------------------------------------------
    # 1. Load
    # --------------------------------------------------------

    df = load_quality_dataset()

    # --------------------------------------------------------
    # 2. Validate
    # --------------------------------------------------------

    df = validate_quality_dataset(df)

    # --------------------------------------------------------
    # 3. Features
    # --------------------------------------------------------

    (
        X,
        numerical_columns,
        categorical_columns
    ) = prepare_features(df)

    # --------------------------------------------------------
    # 4. Targets
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
    # FINAL INFORMATION
    # ========================================================

    print("\n" + "=" * 70)
    print("QUALITY ML DATASET READY")
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

    print("\nRegression targets:")

    for target in REGRESSION_TARGETS:

        print(
            f"  - {target}"
        )

    print("\nClassification targets:")

    for target in CLASSIFICATION_TARGETS:

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

        dataset = prepare_quality_dataset()

        print(
            "\n✓ Quality dataset preparation "
            "completed successfully."
        )

        print(
            "✓ Ready for separate quality "
            "and spoilage models."
        )

    except Exception as e:

        print("\n" + "=" * 70)
        print("QUALITY DATASET PREPARATION FAILED")
        print("=" * 70)

        print(
            f"\nError: {e}"
        )

        sys.exit(1)