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
# DEMAND DATA PREPARATION
# ============================================================

def prepare_demand_data():

    datasets = load_all_datasets()

    demand_df = datasets[
        "demand_arrivals"
    ].copy()

    print("\n" + "=" * 70)
    print("DEMAND FORECASTING DATA PREPROCESSING")
    print("=" * 70)

    print(
        f"\nInitial shape: {demand_df.shape}"
    )

    # --------------------------------------------------------
    # Basic cleaning
    # --------------------------------------------------------

    demand_df = basic_cleaning(
        demand_df,
        dataset_name="DEMAND & ARRIVALS",
        date_columns=["date"]
    )

    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    sort_columns = [
        "district",
        "market",
        "crop",
        "date"
    ]

    existing_sort_columns = [
        column
        for column in sort_columns
        if column in demand_df.columns
    ]

    demand_df = demand_df.sort_values(
        existing_sort_columns
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Target
    # --------------------------------------------------------

    target_column = "next_day_demand_tonnes"

    if target_column not in demand_df.columns:

        raise ValueError(
            f"Target column '{target_column}' not found."
        )

    before_target_cleaning = len(demand_df)

    demand_df = demand_df.dropna(
        subset=[target_column]
    )

    removed_target_rows = (
        before_target_cleaning - len(demand_df)
    )

    print(
        f"\nRows removed due to missing target: "
        f"{removed_target_rows:,}"
    )

    # --------------------------------------------------------
    # Target information
    # --------------------------------------------------------

    print("\nTarget:")
    print("-" * 70)

    print(
        f"Target column: {target_column}"
    )

    print(
        f"Target minimum: "
        f"{demand_df[target_column].min()}"
    )

    print(
        f"Target maximum: "
        f"{demand_df[target_column].max()}"
    )

    print(
        f"Target mean: "
        f"{demand_df[target_column].mean():.2f}"
    )

    # --------------------------------------------------------
    # Feature columns
    # --------------------------------------------------------

    excluded_columns = [
        target_column,
        "demand_id"
    ]

    feature_columns = [
        column
        for column in demand_df.columns
        if column not in excluded_columns
    ]

    print("\nFeature columns:")
    print("-" * 70)

    for column in feature_columns:
        print(f"  - {column}")

    # --------------------------------------------------------
    # Numerical features
    # --------------------------------------------------------

    numerical_columns = get_numerical_columns(
        demand_df[feature_columns]
    )

    print("\nNumerical feature columns:")
    print("-" * 70)

    for column in numerical_columns:
        print(f"  - {column}")

    # --------------------------------------------------------
    # Categorical features
    # --------------------------------------------------------

    categorical_columns = get_categorical_columns(
        demand_df[feature_columns]
    )

    print("\nCategorical feature columns:")
    print("-" * 70)

    for column in categorical_columns:
        print(f"  - {column}")

    # --------------------------------------------------------
    # Final shape
    # --------------------------------------------------------

    print("\nFinal demand dataset shape:")
    print(demand_df.shape)

    print("\n" + "=" * 70)
    print("DEMAND FORECASTING PREPROCESSING COMPLETED")
    print("=" * 70)

    return demand_df


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    demand_df = prepare_demand_data()