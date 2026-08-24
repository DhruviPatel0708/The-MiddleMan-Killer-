from load_weather import load_weather_data


def validate_weather_data(df):

    print("\n" + "=" * 70)
    print("WEATHER DATA VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Basic information
    # --------------------------------------------------------

    print(f"\nRows              : {len(df):,}")
    print(f"Columns           : {len(df.columns)}")

    # --------------------------------------------------------
    # Duplicate records
    # --------------------------------------------------------

    duplicate_count = df.duplicated().sum()

    print(f"Duplicate rows    : {duplicate_count:,}")

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    missing_values = df.isnull().sum()

    total_missing = missing_values.sum()

    print(f"Missing values    : {total_missing:,}")

    if total_missing > 0:
        print("\nMissing values by column:")

        for column, count in missing_values.items():

            if count > 0:
                print(f"  - {column}: {count}")

    # --------------------------------------------------------
    # Data types
    # --------------------------------------------------------

    print("\nData Types:")
    print("-" * 70)

    print(df.dtypes.to_string())

    # --------------------------------------------------------
    # Date validation
    # --------------------------------------------------------

    if "date" in df.columns:

        invalid_dates = df["date"].isna().sum()

        print("\nDate validation:")
        print(f"  Invalid dates : {invalid_dates}")

        if not df["date"].isna().all():

            print(
                f"  Date range    : "
                f"{df['date'].min()} → {df['date'].max()}"
            )

    # --------------------------------------------------------
    # Location information
    # --------------------------------------------------------

    if "district" in df.columns:

        print("\nDistrict information:")
        print(f"  Unique districts : {df['district'].nunique()}")

    if "state" in df.columns:

        print("\nState information:")
        print(f"  Unique states    : {df['state'].nunique()}")

    # --------------------------------------------------------
    # Weather risk
    # --------------------------------------------------------

    if "weather_risk" in df.columns:

        print("\nWeather risk distribution:")
        print("-" * 70)

        print(
            df["weather_risk"]
            .value_counts(dropna=False)
            .to_string()
        )

    # --------------------------------------------------------
    # Numerical weather features
    # --------------------------------------------------------

    numerical_columns = [
        "latitude",
        "longitude",
        "rain_probability",
        "rainfall_mm",
        "temperature_max",
        "temperature_min",
        "visibility_min_m",
        "wind_gust_max",
        "wind_speed_max"
    ]

    print("\nNumerical Weather Features:")
    print("-" * 70)

    for column in numerical_columns:

        if column in df.columns:

            print(
                f"\n{column}:"
            )

            print(
                f"  Min    : {df[column].min()}"
            )

            print(
                f"  Max    : {df[column].max()}"
            )

            print(
                f"  Mean   : {df[column].mean():.2f}"
            )

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("WEATHER DATA VALIDATION COMPLETED")
    print("=" * 70)


def main():

    weather_df = load_weather_data()

    validate_weather_data(weather_df)


if __name__ == "__main__":
    main()