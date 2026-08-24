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
# CROP QUALITY DATA PREPARATION
# ============================================================

def prepare_quality_data():

    datasets = load_all_datasets()

    quality_df = datasets["crop_quality"].copy()

    print("\n" + "=" * 70)
    print("CROP QUALITY DATA PREPROCESSING")
    print("=" * 70)

    print(
        f"\nInitial shape: {quality_df.shape}"
    )

    # --------------------------------------------------------
    # Basic cleaning
    # --------------------------------------------------------

    quality_df = basic_cleaning(
        quality_df,
        dataset_name="CROP QUALITY DATA"
    )

    # --------------------------------------------------------
    # Targets
    # --------------------------------------------------------

    target_columns = [
        "quality_score",
        "quality_grade",
        "spoilage_risk_score",
        "spoilage_risk"
    ]

    print("\nTarget columns:")
    print("-" * 70)

    for column in target_columns:

        if column in quality_df.columns:

            print(f"  - {column}")

    # --------------------------------------------------------
    # Target missing-value check
    # --------------------------------------------------------

    print("\nTarget missing values:")
    print("-" * 70)

    for column in target_columns:

        if column in quality_df.columns:

            print(
                f"  {column}: "
                f"{quality_df[column].isna().sum():,}"
            )

    # --------------------------------------------------------
    # Quality score distribution
    # --------------------------------------------------------

    if "quality_score" in quality_df.columns:

        print("\nQuality score:")
        print("-" * 70)

        print(
            f"Minimum: "
            f"{quality_df['quality_score'].min()}"
        )

        print(
            f"Maximum: "
            f"{quality_df['quality_score'].max()}"
        )

        print(
            f"Mean: "
            f"{quality_df['quality_score'].mean():.2f}"
        )

    # --------------------------------------------------------
    # Quality grade distribution
    # --------------------------------------------------------

    if "quality_grade" in quality_df.columns:

        print("\nQuality grade distribution:")
        print("-" * 70)

        print(
            quality_df["quality_grade"]
            .value_counts(dropna=False)
            .to_string()
        )

    # --------------------------------------------------------
    # Spoilage risk score distribution
    # --------------------------------------------------------

    if "spoilage_risk_score" in quality_df.columns:

        print("\nSpoilage risk score:")
        print("-" * 70)

        print(
            f"Minimum: "
            f"{quality_df['spoilage_risk_score'].min()}"
        )

        print(
            f"Maximum: "
            f"{quality_df['spoilage_risk_score'].max()}"
        )

        print(
            f"Mean: "
            f"{quality_df['spoilage_risk_score'].mean():.2f}"
        )

    # --------------------------------------------------------
    # Spoilage risk distribution
    # --------------------------------------------------------

    if "spoilage_risk" in quality_df.columns:

        print("\nSpoilage risk distribution:")
        print("-" * 70)

        print(
            quality_df["spoilage_risk"]
            .value_counts(dropna=False)
            .to_string()
        )

    # --------------------------------------------------------
    # Exclude identifiers
    # --------------------------------------------------------

    excluded_columns = [
        "quality_id",
        "transaction_id",
        "farmer_id"
    ]

    feature_columns = [
        column
        for column in quality_df.columns
        if column not in excluded_columns
    ]

    print("\nExcluded identifier columns:")
    print("-" * 70)

    for column in excluded_columns:

        if column in quality_df.columns:

            print(f"  - {column}")

    # --------------------------------------------------------
    # Numerical features
    # --------------------------------------------------------

    numerical_columns = get_numerical_columns(
        quality_df[feature_columns]
    )

    print("\nNumerical columns:")
    print("-" * 70)

    for column in numerical_columns:

        print(f"  - {column}")

    # --------------------------------------------------------
    # Categorical features
    # --------------------------------------------------------

    categorical_columns = get_categorical_columns(
        quality_df[feature_columns]
    )

    print("\nCategorical columns:")
    print("-" * 70)

    for column in categorical_columns:

        print(f"  - {column}")

    # --------------------------------------------------------
    # Final shape
    # --------------------------------------------------------

    print("\nFinal quality dataset shape:")
    print(quality_df.shape)

    print("\n" + "=" * 70)
    print("CROP QUALITY DATA PREPROCESSING COMPLETED")
    print("=" * 70)

    return quality_df


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    quality_df = prepare_quality_data()