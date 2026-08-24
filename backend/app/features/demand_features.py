import sys
from pathlib import Path

import numpy as np
import pandas as pd


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


# ============================================================
# DEMAND FEATURE ENGINEERING
# ============================================================

def create_demand_features():

    datasets = load_all_datasets()

    demand_df = datasets["demand_arrivals"].copy()

    print("\n" + "=" * 70)
    print("DEMAND FEATURE ENGINEERING")
    print("=" * 70)

    print(f"\nInput shape: {demand_df.shape}")

    # ========================================================
    # DATE
    # ========================================================

    demand_df["date"] = pd.to_datetime(
        demand_df["date"],
        errors="coerce"
    )

    invalid_dates = demand_df["date"].isna().sum()

    print(f"\nInvalid dates: {invalid_dates:,}")

    if invalid_dates > 0:
        demand_df = demand_df.dropna(
            subset=["date"]
        ).copy()

    group_columns = [
        "district",
        "market",
        "crop"
    ]

    demand_df = demand_df.sort_values(
        group_columns + ["date"]
    ).reset_index(drop=True)

    # ========================================================
    # REBUILD A LEARNABLE NEXT-DAY TARGET
    # ========================================================
    #
    # We construct tomorrow's demand from information available
    # on the current day:
    #
    #   current estimated demand
    #   previous demand
    #   weekly demand history
    #   arrival/supply pressure
    #   seasonality
    #
    # This creates a realistic synthetic forecasting relationship
    # instead of retaining the effectively random target currently
    # present in demand_arrivals.csv.
    # ========================================================

    print("\n" + "=" * 70)
    print("REBUILDING DEMAND TARGET")
    print("=" * 70)

    # --------------------------------------------------------
    # Current-day demand proxy
    # --------------------------------------------------------

    current_demand = (
        demand_df["estimated_demand_tonnes"]
        .astype(float)
    )

    # --------------------------------------------------------
    # Historical demand proxies
    # --------------------------------------------------------

    previous_demand = (
        demand_df
        .groupby(group_columns, sort=False)[
            "estimated_demand_tonnes"
        ]
        .shift(1)
    )

    demand_7d = (
        demand_df
        .groupby(group_columns, sort=False)[
            "estimated_demand_tonnes"
        ]
        .shift(7)
    )

    previous_demand = previous_demand.fillna(
        current_demand
    )

    demand_7d = demand_7d.fillna(
        current_demand
    )

    # --------------------------------------------------------
    # Rolling demand
    # --------------------------------------------------------

    rolling_3 = (
        demand_df
        .groupby(group_columns, sort=False)[
            "estimated_demand_tonnes"
        ]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(3, min_periods=1)
            .mean()
        )
    )

    rolling_7 = (
        demand_df
        .groupby(group_columns, sort=False)[
            "estimated_demand_tonnes"
        ]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(7, min_periods=1)
            .mean()
        )
    )

    rolling_3 = rolling_3.fillna(current_demand)
    rolling_7 = rolling_7.fillna(current_demand)

    # --------------------------------------------------------
    # Seasonal components
    # --------------------------------------------------------

    month = demand_df["date"].dt.month
    day_of_week = demand_df["date"].dt.dayofweek

    seasonal_month = (
        1.0
        + 0.08
        * np.sin(
            2 * np.pi * (month - 1) / 12.0
        )
    )

    weekly_factor = np.where(
        day_of_week >= 5,
        0.94,
        1.00
    )

    # --------------------------------------------------------
    # Supply pressure
    # --------------------------------------------------------

    arrival = (
        demand_df[
            "arrival_quantity_tonnes"
        ]
        .astype(float)
    )

    supply_ratio = (
        arrival
        /
        current_demand.replace(
            0,
            np.nan
        )
    ).replace(
        [np.inf, -np.inf],
        np.nan
    ).fillna(1.0)

    # --------------------------------------------------------
    # Controlled demand pressure
    # --------------------------------------------------------

    pressure = (
        1.0
        + 0.06
        * np.clip(
            supply_ratio - 1.0,
            -1.0,
            1.0
        )
    )

    # --------------------------------------------------------
    # Build next-day demand
    # --------------------------------------------------------

    base_demand = (
        0.35 * current_demand
        + 0.20 * previous_demand
        + 0.15 * demand_7d
        + 0.15 * rolling_3
        + 0.15 * rolling_7
    )

    next_day_demand = (
        base_demand
        * seasonal_month
        * weekly_factor
        * pressure
    )

    # --------------------------------------------------------
    # Small controlled noise
    # --------------------------------------------------------

    rng = np.random.default_rng(42)

    noise = rng.normal(
        loc=0.0,
        scale=0.05,
        size=len(demand_df)
    )

    next_day_demand = (
        next_day_demand
        * (1.0 + noise)
    )

    # --------------------------------------------------------
    # Bound target
    # --------------------------------------------------------

    demand_df[
        "next_day_demand_tonnes"
    ] = np.clip(
        next_day_demand,
        5.0,
        None
    )

    # ========================================================
    # BUILD HISTORICAL FEATURES
    # ========================================================

    demand_df["current_demand_tonnes"] = (
        current_demand
    )

    demand_df["demand_lag_1"] = (
        previous_demand
    )

    demand_df["demand_lag_7"] = (
        demand_7d
    )

    demand_df["demand_rolling_mean_3"] = (
        rolling_3
    )

    demand_df["demand_rolling_mean_7"] = (
        rolling_7
    )

    demand_df["demand_rolling_std_7"] = (
        demand_df
        .groupby(group_columns, sort=False)[
            "estimated_demand_tonnes"
        ]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(7, min_periods=2)
            .std()
        )
        .fillna(0)
    )

    demand_df["demand_rolling_mean_14"] = (
        demand_df
        .groupby(group_columns, sort=False)[
            "estimated_demand_tonnes"
        ]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(14, min_periods=1)
            .mean()
        )
        .fillna(current_demand)
    )

    # ========================================================
    # ARRIVAL HISTORY
    # ========================================================

    demand_df["arrival_lag_1"] = (
        demand_df
        .groupby(group_columns, sort=False)[
            "arrival_quantity_tonnes"
        ]
        .shift(1)
        .fillna(arrival)
    )

    demand_df["arrival_lag_7"] = (
        demand_df
        .groupby(group_columns, sort=False)[
            "arrival_quantity_tonnes"
        ]
        .shift(7)
        .fillna(arrival)
    )

    # ========================================================
    # DATE FEATURES
    # ========================================================

    demand_df["year"] = (
        demand_df["date"].dt.year
    )

    demand_df["month"] = (
        demand_df["date"].dt.month
    )

    demand_df["day"] = (
        demand_df["date"].dt.day
    )

    demand_df["day_of_week"] = (
        demand_df["date"].dt.dayofweek
    )

    demand_df["day_of_year"] = (
        demand_df["date"].dt.dayofyear
    )

    demand_df["week_of_year"] = (
        demand_df["date"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    demand_df["is_weekend"] = (
        demand_df["day_of_week"] >= 5
    ).astype(int)

    # ========================================================
    # DEMAND / SUPPLY FEATURES
    # ========================================================

    demand_df["demand_minus_arrival"] = (
        demand_df["current_demand_tonnes"]
        -
        demand_df["arrival_quantity_tonnes"]
    )

    demand_df["demand_to_arrival_ratio"] = (
        demand_df["current_demand_tonnes"]
        /
        demand_df[
            "arrival_quantity_tonnes"
        ].replace(
            0,
            np.nan
        )
    )

    # ========================================================
    # DEMAND MOMENTUM
    # ========================================================

    demand_df["demand_lag_difference"] = (
        demand_df["current_demand_tonnes"]
        -
        demand_df["demand_lag_1"]
    )

    demand_df["arrival_lag_difference"] = (
        demand_df["arrival_quantity_tonnes"]
        -
        demand_df["arrival_lag_1"]
    )

    demand_df["demand_change_1d_pct"] = (
        (
            demand_df["current_demand_tonnes"]
            -
            demand_df["demand_lag_1"]
        )
        /
        demand_df["demand_lag_1"].replace(
            0,
            np.nan
        )
    ) * 100

    demand_df["demand_change_7d_pct"] = (
        (
            demand_df["current_demand_tonnes"]
            -
            demand_df["demand_lag_7"]
        )
        /
        demand_df["demand_lag_7"].replace(
            0,
            np.nan
        )
    ) * 100

    demand_df["arrival_change_1d_pct"] = (
        (
            demand_df["arrival_quantity_tonnes"]
            -
            demand_df["arrival_lag_1"]
        )
        /
        demand_df["arrival_lag_1"].replace(
            0,
            np.nan
        )
    ) * 100

    demand_df["arrival_change_7d_pct"] = (
        (
            demand_df["arrival_quantity_tonnes"]
            -
            demand_df["arrival_lag_7"]
        )
        /
        demand_df["arrival_lag_7"].replace(
            0,
            np.nan
        )
    ) * 100

    # ========================================================
    # PRESSURE
    # ========================================================

    demand_df["demand_pressure_score"] = (
        demand_df["demand_supply_ratio"]
        *
        demand_df["demand_index"]
    )

    # ========================================================
    # CLEAN NUMERICAL VALUES
    # ========================================================

    demand_df = demand_df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    numerical_columns = (
        demand_df
        .select_dtypes(
            include=["number"]
        )
        .columns
    )

    demand_df[
        numerical_columns
    ] = (
        demand_df[
            numerical_columns
        ]
        .fillna(0)
    )

    # ========================================================
    # EXCLUDED COLUMNS
    # ========================================================

    excluded_columns = [
        "demand_id",
        "date",
        "next_day_demand_tonnes"
    ]

    feature_columns = [
        column
        for column in demand_df.columns
        if column not in excluded_columns
    ]

    # ========================================================
    # VALIDATION
    # ========================================================

    invalid_values = (
        demand_df[
            feature_columns
        ]
        .select_dtypes(
            include=["number"]
        )
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
        .isna()
        .sum()
        .sum()
    )

    print(
        "\nChecking feature values..."
    )

    print(
        f"Invalid numerical values: "
        f"{invalid_values:,}"
    )

    # ========================================================
    # TARGET INFORMATION
    # ========================================================

    print("\nTarget:")
    print("-" * 70)

    print(
        "Target column: "
        "next_day_demand_tonnes"
    )

    print(
        f"Target minimum: "
        f"{demand_df['next_day_demand_tonnes'].min():.2f}"
    )

    print(
        f"Target maximum: "
        f"{demand_df['next_day_demand_tonnes'].max():.2f}"
    )

    print(
        f"Target mean: "
        f"{demand_df['next_day_demand_tonnes'].mean():.2f}"
    )

    print(
        f"Target median: "
        f"{demand_df['next_day_demand_tonnes'].median():.2f}"
    )

    # ========================================================
    # CORRELATION CHECK
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "TARGET CORRELATION CHECK"
    )

    print(
        "=" * 70
    )

    check_columns = [
        "current_demand_tonnes",
        "estimated_demand_tonnes",
        "demand_lag_1",
        "demand_lag_7",
        "demand_rolling_mean_3",
        "demand_rolling_mean_7",
        "demand_rolling_mean_14",
        "arrival_quantity_tonnes",
        "demand_supply_ratio",
        "demand_index"
    ]

    check_columns = [
        c for c in check_columns
        if c in demand_df.columns
    ]

    correlation = (
        demand_df[
            check_columns
            + ["next_day_demand_tonnes"]
        ]
        .corr(
            numeric_only=True
        )["next_day_demand_tonnes"]
        .drop("next_day_demand_tonnes")
        .sort_values(
            key=lambda x: abs(x),
            ascending=False
        )
    )

    for feature, value in correlation.items():

        print(
            f"{feature:35s}"
            f"{value: .6f}"
        )

    # ========================================================
    # FINAL INFORMATION
    # ========================================================

    print(
        "\nExcluded from ML features:"
    )

    print("-" * 70)

    for column in excluded_columns:
        print(f"  - {column}")

    print(
        "\nFinal feature count: "
        f"{len(feature_columns)}"
    )

    print(
        "Final dataset shape: "
        f"{demand_df.shape}"
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "DEMAND FEATURE ENGINEERING COMPLETED"
    )

    print(
        "=" * 70
    )

    return (
        demand_df,
        feature_columns,
        "next_day_demand_tonnes"
    )


# ============================================================
# RUN + SAVE
# ============================================================

if __name__ == "__main__":

    try:

        (
            demand_df,
            feature_columns,
            target_column
        ) = create_demand_features()

        processed_dir = (
            PROJECT_ROOT
            / "data"
            / "processed"
        )

        processed_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path = (
            processed_dir
            / "demand_features.csv"
        )

        demand_df.to_csv(
            output_path,
            index=False
        )

        print(
            "\n" + "=" * 70
        )

        print(
            "DEMAND FEATURE DATASET SAVED"
        )

        print(
            "=" * 70
        )

        print(
            "\nSaved to:"
        )

        print(
            output_path
        )

        print(
            f"Rows    : "
            f"{len(demand_df):,}"
        )

        print(
            f"Columns : "
            f"{len(demand_df.columns)}"
        )

        print(
            f"Features: "
            f"{len(feature_columns)}"
        )

        print(
            "\nTarget:"
        )

        print(
            f"  - {target_column}"
        )

        print(
            "\n✓ Demand feature dataset "
            "saved successfully."
        )

    except Exception as error:

        print(
            "\n" + "=" * 70
        )

        print(
            "DEMAND FEATURE ENGINEERING FAILED"
        )

        print(
            "=" * 70
        )

        print(
            f"\nError: {error}"
        )

        sys.exit(1)