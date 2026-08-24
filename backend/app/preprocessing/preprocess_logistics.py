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
# LOGISTICS DATA PREPARATION
# ============================================================

def prepare_logistics_data():

    datasets = load_all_datasets()

    logistics_df = datasets["logistics"].copy()

    print("\n" + "=" * 70)
    print("LOGISTICS DATA PREPROCESSING")
    print("=" * 70)

    print(
        f"\nInitial shape: {logistics_df.shape}"
    )

    # --------------------------------------------------------
    # Basic cleaning
    # --------------------------------------------------------

    logistics_df = basic_cleaning(
        logistics_df,
        dataset_name="LOGISTICS DATA"
    )

    # --------------------------------------------------------
    # Target candidates
    # --------------------------------------------------------

    target_candidates = [
        "transport_cost",
        "delay_hours",
        "damage_percentage"
    ]

    print("\nPotential logistics targets:")
    print("-" * 70)

    for column in target_candidates:

        if column in logistics_df.columns:

            print(f"  - {column}")

    # --------------------------------------------------------
    # Target missing values
    # --------------------------------------------------------

    print("\nPotential target missing values:")
    print("-" * 70)

    for column in target_candidates:

        if column in logistics_df.columns:

            print(
                f"  {column}: "
                f"{logistics_df[column].isna().sum():,}"
            )

    # --------------------------------------------------------
    # Numerical columns
    # --------------------------------------------------------

    numerical_columns = get_numerical_columns(
        logistics_df
    )

    print("\nNumerical columns:")
    print("-" * 70)

    for column in numerical_columns:

        print(f"  - {column}")

    # --------------------------------------------------------
    # Categorical columns
    # --------------------------------------------------------

    categorical_columns = get_categorical_columns(
        logistics_df
    )

    print("\nCategorical columns:")
    print("-" * 70)

    for column in categorical_columns:

        print(f"  - {column}")

    # --------------------------------------------------------
    # Identifier columns
    # --------------------------------------------------------

    identifier_columns = [
        "logistics_id",
        "transaction_id",
        "farmer_id",
        "buyer_id"
    ]

    print("\nIdentifier columns:")
    print("-" * 70)

    for column in identifier_columns:

        if column in logistics_df.columns:

            print(f"  - {column}")

    # --------------------------------------------------------
    # Final shape
    # --------------------------------------------------------

    print("\nFinal logistics dataset shape:")
    print(logistics_df.shape)

    print("\n" + "=" * 70)
    print("LOGISTICS DATA PREPROCESSING COMPLETED")
    print("=" * 70)

    return logistics_df


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    logistics_df = prepare_logistics_data()