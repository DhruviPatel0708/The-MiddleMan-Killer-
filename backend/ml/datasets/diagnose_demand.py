"""
Demand Dataset Diagnostic

Purpose:
    Diagnose why the demand forecasting model has a negative R².

This script does NOT modify the dataset.
It only analyzes the existing demand_features.csv.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "demand_features.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

TARGET = "next_day_demand_tonnes"

ID_COLUMNS = [
    "demand_id"
]

DATE_COLUMN = "date"

GROUP_COLUMNS = [
    "district",
    "market",
    "crop"
]

LAG_COLUMNS = [
    "demand_lag_1",
    "demand_lag_7",
    "arrival_lag_1",
    "arrival_lag_7"
]

IMPORTANT_FEATURES = [
    "arrival_quantity_tonnes",
    "estimated_demand_tonnes",
    "demand_supply_ratio",
    "demand_index",
    "demand_lag_1",
    "demand_lag_7",
    "arrival_lag_1",
    "arrival_lag_7",
    "arrival_change_1d_pct",
    "arrival_change_7d_pct",
    "demand_change_7d_pct",
    "demand_minus_arrival",
    "demand_to_arrival_ratio",
    "demand_lag_difference",
    "arrival_lag_difference",
    "demand_pressure_score"
]


# ============================================================
# HELPER
# ============================================================

def section(title):

    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# MAIN DIAGNOSTIC
# ============================================================

def diagnose_demand():

    section("DEMAND DATASET DIAGNOSTIC")

    # ========================================================
    # LOAD DATA
    # ========================================================

    print("\nDataset path:")
    print(DATA_PATH)

    if not DATA_PATH.exists():

        raise FileNotFoundError(
            f"\nDemand feature dataset not found:\n{DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    print("\nDataset loaded successfully.")

    print(f"Rows    : {len(df):,}")
    print(f"Columns : {len(df.columns)}")

    # ========================================================
    # BASIC INFORMATION
    # ========================================================

    section("1. BASIC DATA CHECK")

    print("\nColumns:")

    for column in df.columns:
        print(f"  - {column}")

    print("\nData types:")

    print(df.dtypes)

    # ========================================================
    # TARGET CHECK
    # ========================================================

    section("2. TARGET CHECK")

    if TARGET not in df.columns:

        raise ValueError(
            f"Target column '{TARGET}' not found."
        )

    print(f"\nTarget: {TARGET}")

    print(
        f"Missing values : "
        f"{df[TARGET].isna().sum()}"
    )

    print(
        f"Minimum        : "
        f"{df[TARGET].min():.4f}"
    )

    print(
        f"Maximum        : "
        f"{df[TARGET].max():.4f}"
    )

    print(
        f"Mean           : "
        f"{df[TARGET].mean():.4f}"
    )

    print(
        f"Median         : "
        f"{df[TARGET].median():.4f}"
    )

    print(
        f"Std            : "
        f"{df[TARGET].std():.4f}"
    )

    print("\nTarget percentiles:")

    print(
        df[TARGET].quantile(
            [0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]
        )
    )

    # ========================================================
    # DATE CHECK
    # ========================================================

    section("3. DATE CHECK")

    if DATE_COLUMN in df.columns:

        df[DATE_COLUMN] = pd.to_datetime(
            df[DATE_COLUMN],
            errors="coerce"
        )

        print(
            f"\nInvalid dates: "
            f"{df[DATE_COLUMN].isna().sum()}"
        )

        print(
            f"Minimum date : "
            f"{df[DATE_COLUMN].min()}"
        )

        print(
            f"Maximum date : "
            f"{df[DATE_COLUMN].max()}"
        )

        print(
            f"Unique dates : "
            f"{df[DATE_COLUMN].nunique()}"
        )

    # ========================================================
    # DUPLICATE CHECK
    # ========================================================

    section("4. DUPLICATE CHECK")

    print(
        f"\nComplete duplicate rows: "
        f"{df.duplicated().sum():,}"
    )

    available_group_columns = [
        column
        for column in GROUP_COLUMNS
        if column in df.columns
    ]

    if DATE_COLUMN in df.columns:

        duplicate_keys = (
            available_group_columns
            + [DATE_COLUMN]
        )

        duplicate_count = df.duplicated(
            subset=duplicate_keys
        ).sum()

        print(
            f"Duplicate "
            f"(district, market, crop, date) rows: "
            f"{duplicate_count:,}"
        )

    # ========================================================
    # FEATURE MISSING VALUES
    # ========================================================

    section("5. FEATURE MISSING VALUES")

    missing = df.isna().sum()

    missing = missing[
        missing > 0
    ].sort_values(
        ascending=False
    )

    if len(missing) == 0:

        print("\nNo missing values found.")

    else:

        print("\nMissing values:")

        print(missing)

    # ========================================================
    # NUMERICAL CORRELATION
    # ========================================================

    section("6. TARGET CORRELATION")

    numerical_columns = (
        df.select_dtypes(
            include=np.number
        ).columns.tolist()
    )

    numerical_columns = [
        column
        for column in numerical_columns
        if column != TARGET
    ]

    correlation = (
        df[
            numerical_columns
            + [TARGET]
        ]
        .corr(numeric_only=True)[TARGET]
        .drop(TARGET)
        .sort_values(
            key=lambda x: abs(x),
            ascending=False
        )
    )

    print(
        "\nNumerical feature correlations "
        "with target:"
    )

    print(
        correlation.to_string()
    )

    # ========================================================
    # IMPORTANT FEATURE CORRELATIONS
    # ========================================================

    section("7. IMPORTANT DEMAND FEATURE CHECK")

    existing_features = [
        feature
        for feature in IMPORTANT_FEATURES
        if feature in df.columns
    ]

    important_corr = (
        df[
            existing_features
            + [TARGET]
        ]
        .corr(numeric_only=True)[TARGET]
        .drop(TARGET)
        .sort_values(
            key=lambda x: abs(x),
            ascending=False
        )
    )

    print(
        "\nImportant feature correlations:"
    )

    for feature, value in important_corr.items():

        print(
            f"{feature:35s} "
            f"{value: .6f}"
        )

    # ========================================================
    # LAG FEATURE STATISTICS
    # ========================================================

    section("8. LAG FEATURE CHECK")

    existing_lags = [
        column
        for column in LAG_COLUMNS
        if column in df.columns
    ]

    for column in existing_lags:

        print(f"\n{column}")

        print(
            f"  Missing : "
            f"{df[column].isna().sum():,}"
        )

        print(
            f"  Min     : "
            f"{df[column].min():.4f}"
        )

        print(
            f"  Max     : "
            f"{df[column].max():.4f}"
        )

        print(
            f"  Mean    : "
            f"{df[column].mean():.4f}"
        )

        print(
            f"  Corr    : "
            f"{df[column].corr(df[TARGET]):.6f}"
        )

    # ========================================================
    # GROUP INFORMATION
    # ========================================================

    section("9. GROUP INFORMATION")

    for column in GROUP_COLUMNS:

        if column in df.columns:

            print(
                f"{column:15s}: "
                f"{df[column].nunique():,} unique values"
            )

    # ========================================================
    # TARGET VARIATION BY GROUP
    # ========================================================

    section("10. TARGET VARIATION")

    if (
        "crop" in df.columns
        and "district" in df.columns
    ):

        grouped = (
            df.groupby(
                ["district", "crop"]
            )[TARGET]
            .agg(
                [
                    "count",
                    "mean",
                    "std",
                    "min",
                    "max"
                ]
            )
            .sort_values(
                "std",
                ascending=False
            )
        )

        print(
            "\nHighest target variation groups:"
        )

        print(
            grouped.head(10)
        )

    # ========================================================
    # TARGET VS ESTIMATED DEMAND
    # ========================================================

    section("11. ESTIMATED DEMAND CHECK")

    if "estimated_demand_tonnes" in df.columns:

        correlation = (
            df[
                "estimated_demand_tonnes"
            ].corr(
                df[TARGET]
            )
        )

        print(
            "\nCorrelation between "
            "estimated_demand_tonnes and target:"
        )

        print(
            f"{correlation:.6f}"
        )

        print(
            "\nComparison:"
        )

        comparison = df[
            [
                "estimated_demand_tonnes",
                TARGET
            ]
        ].head(20)

        print(
            comparison.to_string(
                index=False
            )
        )

    # ========================================================
    # RANDOM SAMPLE
    # ========================================================

    section("12. RANDOM SAMPLE")

    sample_columns = [
        column
        for column in (
            GROUP_COLUMNS
            + [
                DATE_COLUMN,
                "demand_lag_1",
                "demand_lag_7",
                "estimated_demand_tonnes",
                TARGET
            ]
        )
        if column in df.columns
    ]

    print(
        df[
            sample_columns
        ]
        .sample(
            min(15, len(df)),
            random_state=42
        )
        .to_string(
            index=False
        )
    )

    # ========================================================
    # CONCLUSION
    # ========================================================

    section("DIAGNOSTIC COMPLETED")

    print(
        "\nNo data has been modified."
    )

    print(
        "Use the output above to determine "
        "why the demand model has negative R²."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        diagnose_demand()

        print(
            "\n✓ Demand dataset diagnosis completed."
        )

    except Exception as error:

        print(
            "\n" + "=" * 70
        )

        print(
            "DEMAND DIAGNOSTIC FAILED"
        )

        print(
            "=" * 70
        )

        print(
            f"\nError: {error}"
        )

        sys.exit(1)