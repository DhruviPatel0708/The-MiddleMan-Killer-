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
# TRANSACTION DATA PREPARATION
# ============================================================

def prepare_transaction_data():

    datasets = load_all_datasets()

    transaction_df = datasets[
        "transactions"
    ].copy()

    print("\n" + "=" * 70)
    print("TRANSACTION DATA PREPROCESSING")
    print("=" * 70)

    print(
        f"\nInitial shape: {transaction_df.shape}"
    )

    # --------------------------------------------------------
    # Basic cleaning
    # --------------------------------------------------------

    transaction_df = basic_cleaning(
        transaction_df,
        dataset_name="TRANSACTION DATA",
        date_columns=["transaction_date"]
    )

    # --------------------------------------------------------
    # Transaction status information
    # --------------------------------------------------------

    status_columns = [
        "payment_status",
        "delivery_status"
    ]

    print("\nStatus distributions:")
    print("-" * 70)

    for column in status_columns:

        if column in transaction_df.columns:

            print(f"\n{column}:")

            print(
                transaction_df[column]
                .value_counts(dropna=False)
                .to_string()
            )

    # --------------------------------------------------------
    # Numerical columns
    # --------------------------------------------------------

    numerical_columns = get_numerical_columns(
        transaction_df
    )

    print("\nNumerical columns:")
    print("-" * 70)

    for column in numerical_columns:

        print(f"  - {column}")

    # --------------------------------------------------------
    # Categorical columns
    # --------------------------------------------------------

    categorical_columns = get_categorical_columns(
        transaction_df
    )

    print("\nCategorical columns:")
    print("-" * 70)

    for column in categorical_columns:

        print(f"  - {column}")

    # --------------------------------------------------------
    # Identifier columns
    # --------------------------------------------------------

    identifier_columns = [
        "transaction_id",
        "farmer_id",
        "buyer_id"
    ]

    print("\nIdentifier columns:")
    print("-" * 70)

    for column in identifier_columns:

        if column in transaction_df.columns:

            print(f"  - {column}")

    # --------------------------------------------------------
    # Final shape
    # --------------------------------------------------------

    print("\nFinal transaction dataset shape:")
    print(transaction_df.shape)

    print("\n" + "=" * 70)
    print("TRANSACTION DATA PREPROCESSING COMPLETED")
    print("=" * 70)

    return transaction_df


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    transaction_df = prepare_transaction_data()