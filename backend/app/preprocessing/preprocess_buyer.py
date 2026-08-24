import sys
from pathlib import Path

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

from backend.app.data.load_datasets import load_all_datasets

from backend.app.preprocessing.utils import (
    basic_cleaning,
    get_numerical_columns,
    get_categorical_columns
)


# ============================================================
# BUYER RELIABILITY DATA PREPARATION
# ============================================================

def prepare_buyer_data():

    datasets = load_all_datasets()

    buyer_df = datasets["buyers"].copy()

    print("\n" + "=" * 70)
    print("BUYER RELIABILITY DATA PREPROCESSING")
    print("=" * 70)

    print(
        f"\nInitial shape: {buyer_df.shape}"
    )

    # --------------------------------------------------------
    # Basic cleaning
    # --------------------------------------------------------

    buyer_df = basic_cleaning(
        buyer_df,
        dataset_name="BUYER DATA"
    )

    # --------------------------------------------------------
    # Target
    # --------------------------------------------------------

    target_column = "buyer_reliability_label"

    if target_column not in buyer_df.columns:

        raise ValueError(
            f"Target column '{target_column}' not found."
        )

    # --------------------------------------------------------
    # Target missing values
    # --------------------------------------------------------

    before_target_cleaning = len(buyer_df)

    buyer_df = buyer_df.dropna(
        subset=[target_column]
    )

    removed_target_rows = (
        before_target_cleaning - len(buyer_df)
    )

    print(
        f"\nRows removed due to missing target: "
        f"{removed_target_rows:,}"
    )

    # --------------------------------------------------------
    # Target distribution
    # --------------------------------------------------------

    print("\nTarget distribution:")
    print("-" * 70)

    print(
        buyer_df[target_column]
        .value_counts(dropna=False)
        .to_string()
    )

    # --------------------------------------------------------
    # Remove direct leakage fields
    # --------------------------------------------------------

    excluded_columns = [
        "buyer_id",
        "buyer_name",
        "buyer_reliability_label",
        "reliability_score"
    ]
    feature_columns = [
        column
        for column in buyer_df.columns
        if column not in excluded_columns
    ]

    print("\nExcluded columns:")
    print("-" * 70)

    for column in excluded_columns:

        if column in buyer_df.columns:
            print(f"  - {column}")

    # --------------------------------------------------------
    # Feature columns
    # --------------------------------------------------------

    print("\nFeature columns:")
    print("-" * 70)

    for column in feature_columns:

        print(f"  - {column}")

    # --------------------------------------------------------
    # Numerical features
    # --------------------------------------------------------

    numerical_columns = get_numerical_columns(
        buyer_df[feature_columns]
    )

    print("\nNumerical feature columns:")
    print("-" * 70)

    for column in numerical_columns:

        print(f"  - {column}")

    # --------------------------------------------------------
    # Categorical features
    # --------------------------------------------------------

    categorical_columns = get_categorical_columns(
        buyer_df[feature_columns]
    )

    print("\nCategorical feature columns:")
    print("-" * 70)

    for column in categorical_columns:

        print(f"  - {column}")

    # --------------------------------------------------------
    # Final shape
    # --------------------------------------------------------

    print("\nFinal buyer dataset shape:")
    print(buyer_df.shape)

    print("\n" + "=" * 70)
    print("BUYER RELIABILITY PREPROCESSING COMPLETED")
    print("=" * 70)

    return buyer_df


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    buyer_df = prepare_buyer_data()