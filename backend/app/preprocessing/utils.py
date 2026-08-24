import pandas as pd


# ============================================================
# CHECK DATAFRAME
# ============================================================

def check_dataframe(df, dataset_name="dataset"):

    if df is None:
        raise ValueError(f"{dataset_name} is None.")

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"{dataset_name} must be a pandas DataFrame."
        )

    if df.empty:
        raise ValueError(
            f"{dataset_name} is empty."
        )

    return True


# ============================================================
# CONVERT DATE COLUMNS
# ============================================================

def convert_date_columns(df, date_columns):

    df = df.copy()

    for column in date_columns:

        if column in df.columns:

            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    return df


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def remove_duplicates(df):

    df = df.copy()

    before = len(df)

    df = df.drop_duplicates()

    after = len(df)

    removed = before - after

    print(
        f"Duplicate rows removed: {removed:,}"
    )

    return df


# ============================================================
# MISSING VALUE SUMMARY
# ============================================================

def missing_value_summary(df):

    missing = df.isnull().sum()

    missing = missing[missing > 0]

    if missing.empty:

        print("Missing values: 0")

    else:

        print("\nMissing values:")

        for column, count in missing.items():

            print(
                f"  - {column}: {count:,}"
            )

    return missing


# ============================================================
# NUMERICAL COLUMN DETECTION
# ============================================================

def get_numerical_columns(df):

    return df.select_dtypes(
        include=["number"]
    ).columns.tolist()


# ============================================================
# CATEGORICAL COLUMN DETECTION
# ============================================================

def get_categorical_columns(df):

    return df.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()


# ============================================================
# BASIC DATAFRAME CLEANING
# ============================================================

def basic_cleaning(
    df,
    dataset_name="dataset",
    date_columns=None
):

    print("\n" + "=" * 70)
    print(f"PREPROCESSING: {dataset_name}")
    print("=" * 70)

    check_dataframe(
        df,
        dataset_name
    )

    print(
        f"Initial shape: {df.shape}"
    )

    # Remove exact duplicate rows
    df = remove_duplicates(df)

    # Convert date columns
    if date_columns:

        df = convert_date_columns(
            df,
            date_columns
        )

    # Missing-value report
    missing_value_summary(df)

    print(
        f"Final shape: {df.shape}"
    )

    print("=" * 70)

    return df