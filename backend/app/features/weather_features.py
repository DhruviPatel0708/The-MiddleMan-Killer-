import sys
from pathlib import Path

import pandas as pd


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORT WEATHER LOADER
# ============================================================

from backend.app.data.load_weather import load_weather_data


# ============================================================
# WEATHER FEATURE ENGINEERING
# ============================================================

def create_weather_features():

    weather_df = load_weather_data().copy()

    print("\n" + "=" * 70)
    print("WEATHER FEATURE ENGINEERING")
    print("=" * 70)

    print(
        f"\nInput shape: {weather_df.shape}"
    )

    # ========================================================
    # DATE CONVERSION
    # ========================================================

    weather_df["date"] = pd.to_datetime(
        weather_df["date"],
        errors="coerce"
    )

    # ========================================================
    # CHECK DATE VALUES
    # ========================================================

    invalid_dates = weather_df["date"].isna().sum()

    print(
        f"\nInvalid dates: {invalid_dates:,}"
    )

    if invalid_dates != 0:

        raise ValueError(
            "Invalid weather dates found."
        )

    # ========================================================
    # DATE FEATURES
    # ========================================================

    weather_df["year"] = (
        weather_df["date"].dt.year
    )

    weather_df["month"] = (
        weather_df["date"].dt.month
    )

    weather_df["day"] = (
        weather_df["date"].dt.day
    )

    weather_df["day_of_week"] = (
        weather_df["date"].dt.dayofweek
    )

    weather_df["day_of_year"] = (
        weather_df["date"].dt.dayofyear
    )

    weather_df["is_weekend"] = (
        weather_df["day_of_week"] >= 5
    ).astype(int)

    # ========================================================
    # TEMPERATURE FEATURES
    # ========================================================

    weather_df["temperature_range"] = (
        weather_df["temperature_max"]
        -
        weather_df["temperature_min"]
    )

    # ========================================================
    # RAIN FEATURES
    # ========================================================

    weather_df["rainfall_intensity"] = (
        weather_df["rainfall_mm"]
        *
        weather_df["rain_probability"]
        /
        100
    )

    # ========================================================
    # WIND FEATURES
    # ========================================================

    weather_df["wind_gust_difference"] = (
        weather_df["wind_gust_max"]
        -
        weather_df["wind_speed_max"]
    )

    # ========================================================
    # WEATHER STRESS FEATURES
    # ========================================================

    weather_df["temperature_stress"] = (
        weather_df["temperature_max"]
        -
        weather_df["temperature_min"]
    )

    weather_df["visibility_risk"] = (
        weather_df["visibility_min_m"] < 5000
    ).astype(int)

    # ========================================================
    # EXCLUDED COLUMNS
    # ========================================================

    excluded_columns = [
        "date",
        "updated_at",
        "source"
    ]

    # ========================================================
    # FEATURE COLUMNS
    # ========================================================

    feature_columns = [
        column
        for column in weather_df.columns
        if column not in excluded_columns
    ]

    # ========================================================
    # NUMERICAL FEATURES
    # ========================================================

    numerical_columns = [
        column
        for column in feature_columns
        if pd.api.types.is_numeric_dtype(
            weather_df[column]
        )
    ]

    # ========================================================
    # CATEGORICAL FEATURES
    # ========================================================

    categorical_columns = [
        "district",
        "state",
        "weather_risk"
    ]

    categorical_columns = [
        column
        for column in categorical_columns
        if column in weather_df.columns
    ]

    # ========================================================
    # CHECK INVALID NUMERICAL VALUES
    # ========================================================

    print("\nChecking feature values...")

    numerical_features = weather_df[
        numerical_columns
    ].copy()

    numerical_features = numerical_features.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    invalid_values = (
        numerical_features
        .isna()
        .sum()
        .sum()
    )

    print(
        f"Invalid numerical values: "
        f"{invalid_values:,}"
    )

    # ========================================================
    # WEATHER RISK DISTRIBUTION
    # ========================================================

    print("\nWeather risk distribution:")
    print("-" * 70)

    print(
        weather_df["weather_risk"]
        .value_counts()
        .to_string()
    )

    # ========================================================
    # DISTRICT INFORMATION
    # ========================================================

    print("\nDistrict information:")
    print("-" * 70)

    print(
        f"Unique districts: "
        f"{weather_df['district'].nunique()}"
    )

    print(
        f"Unique states: "
        f"{weather_df['state'].nunique()}"
    )

    # ========================================================
    # EXCLUDED COLUMNS
    # ========================================================

    print("\nExcluded from ML features:")
    print("-" * 70)

    for column in excluded_columns:

        if column in weather_df.columns:

            print(f"  - {column}")

    # ========================================================
    # NUMERICAL FEATURES
    # ========================================================

    print("\nNumerical feature columns:")
    print("-" * 70)

    for column in numerical_columns:

        print(f"  - {column}")

    # ========================================================
    # CATEGORICAL FEATURES
    # ========================================================

    print("\nCategorical feature columns:")
    print("-" * 70)

    for column in categorical_columns:

        print(f"  - {column}")

    # ========================================================
    # SANITY CHECK
    # ========================================================

    if invalid_values != 0:

        raise ValueError(
            "Invalid numerical values remain "
            "after weather feature engineering."
        )

    # ========================================================
    # FINAL INFORMATION
    # ========================================================

    print(
        f"\nFinal feature count: "
        f"{len(feature_columns)}"
    )

    print(
        f"Final dataset shape: "
        f"{weather_df.shape}"
    )

    print("\n" + "=" * 70)
    print("WEATHER FEATURE ENGINEERING COMPLETED")
    print("=" * 70)

    return (
        weather_df,
        feature_columns
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    weather_df, feature_columns = (
        create_weather_features()
    )

    print(
        "\nWeather feature engineering test completed."
    )