from load_datasets import load_all_datasets


def summarize_dataset(name, df):

    print("\n" + "=" * 80)
    print(f"DATASET: {name.upper()}")
    print("=" * 80)

    print(f"\nShape: {df.shape}")

    print("\nData Types:")
    print("-" * 80)

    print(df.dtypes.to_string())

    print("\nNumerical Columns:")
    print("-" * 80)

    numerical_columns = df.select_dtypes(
        include=["int64", "float64", "int32", "float32"]
    ).columns.tolist()

    for column in numerical_columns:
        print(f"  - {column}")

    print("\nCategorical/Object Columns:")
    print("-" * 80)

    categorical_columns = df.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    for column in categorical_columns:
        print(f"  - {column}")

    print("\nUnique Values:")
    print("-" * 80)

    for column in df.columns:

        unique_count = df[column].nunique()

        print(
            f"  {column:<40} "
            f"{unique_count:>10,} unique values"
        )

    print("\nStatistical Summary:")
    print("-" * 80)

    print(df.describe(include="all").transpose().to_string())


def main():

    datasets = load_all_datasets()

    print("\n")
    print("#" * 80)
    print("#             AGRICULTURE AI DATA SUMMARY")
    print("#" * 80)

    for name, df in datasets.items():
        summarize_dataset(name, df)

    print("\n")
    print("#" * 80)
    print("#             DATA SUMMARY COMPLETED")
    print("#" * 80)


if __name__ == "__main__":
    main()