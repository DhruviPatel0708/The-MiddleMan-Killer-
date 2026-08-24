import sys
from pathlib import Path

import pandas as pd
import numpy as np


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# LOAD DATA
# ============================================================

from backend.app.data.load_datasets import load_all_datasets


# ============================================================
# CHECK TARGET GENERATION
# ============================================================

def check_demand_target():

    datasets = load_all_datasets()

    df = datasets["demand_arrivals"].copy()

    print("\n" + "=" * 70)
    print("DEMAND TARGET GENERATION CHECK")
    print("=" * 70)

    print(
        f"\nRows    : {len(df):,}"
    )

    print(
        f"Columns : {len(df.columns)}"
    )

    print("\nColumns:")

    for column in df.columns:
        print(f"  - {column}")

    # ========================================================
    # DATE
    # ========================================================

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    group_columns = [
        "district",
        "market",
        "crop"
    ]

    df = df.sort_values(
        group_columns + ["date"]
    ).reset_index(drop=True)

    target = "next_day_demand_tonnes"

    # ========================================================
    # TARGET STATISTICS
    # ========================================================

    print("\n" + "=" * 70)
    print("TARGET STATISTICS")
    print("=" * 70)

    print(
        f"\nTarget: {target}"
    )

    print(
        f"Minimum : {df[target].min():.4f}"
    )

    print(
        f"Maximum : {df[target].max():.4f}"
    )

    print(
        f"Mean    : {df[target].mean():.4f}"
    )

    print(
        f"Median  : {df[target].median():.4f}"
    )

    # ========================================================
    # EXISTING DEMAND COLUMNS
    # ========================================================

    print("\n" + "=" * 70)
    print("POTENTIAL SOURCE FEATURES")
    print("=" * 70)

    potential_features = [
        "arrival_quantity_tonnes",
        "estimated_demand_tonnes",
        "demand_supply_ratio",
        "demand_index",
        "demand_lag_1",
        "demand_lag_7",
        "arrival_lag_1",
        "arrival_lag_7"
    ]

    for feature in potential_features:

        if feature in df.columns:

            correlation = df[
                feature
            ].corr(
                df[target]
            )

            print(
                f"{feature:35s}"
                f"{correlation: .6f}"
            )

    # ========================================================
    # ACTUAL PREVIOUS TARGET
    # ========================================================

    print("\n" + "=" * 70)
    print("ACTUAL PREVIOUS TARGET RELATIONSHIP")
    print("=" * 70)

    df["previous_target"] = (
        df.groupby(
            group_columns,
            sort=False
        )[target]
        .shift(1)
    )

    df["target_7_steps_back"] = (
        df.groupby(
            group_columns,
            sort=False
        )[target]
        .shift(7)
    )

    print(
        "\nPrevious target correlation:"
    )

    print(
        df[
            "previous_target"
        ].corr(
            df[target]
        )
    )

    print(
        "\n7-step previous target correlation:"
    )

    print(
        df[
            "target_7_steps_back"
        ].corr(
            df[target]
        )
    )

    # ========================================================
    # SAMPLE SEQUENCE
    # ========================================================

    print("\n" + "=" * 70)
    print("DEMAND SEQUENCE SAMPLE")
    print("=" * 70)

    sample_group = (
        df.groupby(
            group_columns
        )
        .size()
        .sort_values(
            ascending=False
        )
        .index[0]
    )

    sample = df[
        (
            df["district"]
            == sample_group[0]
        )
        &
        (
            df["market"]
            == sample_group[1]
        )
        &
        (
            df["crop"]
            == sample_group[2]
        )
    ].copy()

    sample = sample.sort_values(
        "date"
    ).head(20)

    columns = [
        "date",
        "arrival_quantity_tonnes",
        "estimated_demand_tonnes",
        "demand_lag_1",
        "demand_lag_7",
        "next_day_demand_tonnes"
    ]

    columns = [
        c for c in columns
        if c in sample.columns
    ]

    print(
        sample[
            columns
        ].to_string(
            index=False
        )
    )

    # ========================================================
    # TARGET UNIQUENESS
    # ========================================================

    print("\n" + "=" * 70)
    print("TARGET UNIQUENESS CHECK")
    print("=" * 70)

    print(
        f"\nUnique target values: "
        f"{df[target].nunique():,}"
    )

    print(
        f"Duplicate target values: "
        f"{df[target].duplicated().sum():,}"
    )

    # ========================================================
    # RANDOMNESS CHECK
    # ========================================================

    print("\n" + "=" * 70)
    print("TARGET AUTOCORRELATION")
    print("=" * 70)

    target_values = df[target].dropna()

    print(
        f"\nLag-1 global autocorrelation: "
        f"{target_values.autocorr(lag=1):.6f}"
    )

    print(
        f"Lag-7 global autocorrelation: "
        f"{target_values.autocorr(lag=7):.6f}"
    )

    print("\n" + "=" * 70)
    print("TARGET CHECK COMPLETED")
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    try:

        check_demand_target()

        print(
            "\n✓ Demand target diagnosis completed."
        )

    except Exception as error:

        print(
            "\n" + "=" * 70
        )

        print(
            "TARGET CHECK FAILED"
        )

        print(
            "=" * 70
        )

        print(
            f"\nError: {error}"
        )

        sys.exit(1)