import sys
from pathlib import Path

import pandas as pd


# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.app.preprocessing.utils import (
    check_dataframe,
    convert_date_columns,
    remove_duplicates,
    missing_value_summary,
    get_numerical_columns,
    get_categorical_columns,
    basic_cleaning
)


def main():

    # Small test dataframe
    test_df = pd.DataFrame({
        "date": [
            "2026-01-01",
            "2026-01-02",
            "2026-01-02"
        ],
        "crop": [
            "Wheat",
            "Rice",
            "Rice"
        ],
        "price": [
            2500,
            3000,
            3000
        ]
    })

    print("\nTesting preprocessing utilities...")

    cleaned_df = basic_cleaning(
        test_df,
        dataset_name="TEST DATASET",
        date_columns=["date"]
    )

    print("\nNumerical columns:")
    print(
        get_numerical_columns(cleaned_df)
    )

    print("\nCategorical columns:")
    print(
        get_categorical_columns(cleaned_df)
    )

    print("\nFinal DataFrame:")
    print(cleaned_df)

    print("\nPreprocessing utilities test completed successfully.")


if __name__ == "__main__":
    main()