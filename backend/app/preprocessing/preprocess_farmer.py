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
# FARMER DATA PREPARATION
# ============================================================

def prepare_farmer_data():

    datasets = load_all_datasets()

    farmer_df = datasets["farmers"].copy()

    print("\n" + "=" * 70)
    print("FARMER DATA PREPROCESSING")
    print("=" * 70)

    print(
        f"\nInitial shape: {farmer_df.shape}"
    )

    # --------------------------------------------------------
    # Basic cleaning
    # --------------------------------------------------------

    farmer_df = basic_cleaning(
        farmer_df,
        dataset_name="FARMER DATA",
        date_columns=[
            "sowing_date",
            "expected_harvest_date",
            "preferred_selling_date"
        ]
    )

    # --------------------------------------------------------
    # Important farmer fields
    # --------------------------------------------------------

    print("\nFarmer crops:")
    print("-" * 70)

    if "crop" in farmer_df.columns:

        print(
            farmer_df["crop"]
            .value_counts(dropna=False)
            .to_string()
        )

    # --------------------------------------------------------
    # Quality grade
    # --------------------------------------------------------

    if "quality_grade" in farmer_df.columns:

        print("\nQuality grade distribution:")
        print("-" * 70)

        print(
            farmer_df["quality_grade"]
            .value_counts(dropna=False)
            .to_string()
        )

    # --------------------------------------------------------
    # Storage availability
    # --------------------------------------------------------

    if "storage_available" in farmer_df.columns:

        print("\nStorage availability:")
        print("-" * 70)

        print(
            farmer_df["storage_available"]
            .value_counts(dropna=False)
            .to_string()
        )

    # --------------------------------------------------------
    # Numerical columns
    # --------------------------------------------------------

    numerical_columns = get_numerical_columns(
        farmer_df
    )

    print("\nNumerical columns:")
    print("-" * 70)

    for column in numerical_columns:

        print(f"  - {column}")

    # --------------------------------------------------------
    # Categorical columns
    # --------------------------------------------------------

    categorical_columns = get_categorical_columns(
        farmer_df
    )

    print("\nCategorical columns:")
    print("-" * 70)

    for column in categorical_columns:

        print(f"  - {column}")

    # --------------------------------------------------------
    # Identifier columns
    # --------------------------------------------------------

    identifier_columns = [
        "farmer_id",
        "farmer_name"
    ]

    print("\nIdentifier columns:")
    print("-" * 70)

    for column in identifier_columns:

        if column in farmer_df.columns:

            print(f"  - {column}")

    # --------------------------------------------------------
    # Final shape
    # --------------------------------------------------------

    print("\nFinal farmer dataset shape:")
    print(farmer_df.shape)

    print("\n" + "=" * 70)
    print("FARMER DATA PREPROCESSING COMPLETED")
    print("=" * 70)

    return farmer_df


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    farmer_df = prepare_farmer_data()