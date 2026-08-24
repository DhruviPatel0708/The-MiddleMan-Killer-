"""
Crop Quality Feature Engineering

Input:
    data/raw/crop_quality.csv

Output:
    data/processed/quality_features.csv

Targets:
    quality_score
    quality_grade
    spoilage_risk_score
    spoilage_risk
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORT DATA LOADER
# ============================================================

from backend.app.data.load_datasets import load_all_datasets


# ============================================================
# CONFIGURATION
# ============================================================

TARGET_COLUMNS = [
    "quality_score",
    "quality_grade",
    "spoilage_risk_score",
    "spoilage_risk",
]

EXCLUDED_COLUMNS = [
    "quality_id",
    "transaction_id",
    "farmer_id",
    "quality_score",
    "quality_grade",
    "spoilage_risk_score",
    "spoilage_risk",
]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "quality_features.csv"
)


# ============================================================
# CREATE QUALITY FEATURES
# ============================================================

def create_quality_features():

    datasets = load_all_datasets()

    quality_df = (
        datasets["crop_quality"]
        .copy()
    )

    print("\n" + "=" * 70)
    print("QUALITY FEATURE ENGINEERING")
    print("=" * 70)

    print(
        f"\nInput shape: "
        f"{quality_df.shape}"
    )

    # ========================================================
    # REQUIRED COLUMN CHECK
    # ========================================================

    required_columns = [
        "quality_id",
        "transaction_id",
        "farmer_id",
        "crop",
        "quantity_kg",
        "moisture_percentage",
        "foreign_matter_percentage",
        "damaged_percentage",
        "discolored_percentage",
        "insect_damage_percentage",
        "grain_size",
        "weight_uniformity_percentage",
        "storage_days",
        "storage_temperature_c",
        "storage_humidity_percentage",
        "quality_score",
        "quality_grade",
        "spoilage_risk_score",
        "spoilage_risk",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in quality_df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing quality dataset columns:\n"
            f"{missing_columns}"
        )

    # ========================================================
    # TARGET MISSING VALUES
    # ========================================================

    print("\nTarget missing values:")
    print("-" * 70)

    for target in TARGET_COLUMNS:

        missing = (
            quality_df[target]
            .isna()
            .sum()
        )

        print(
            f"{target}: {missing:,}"
        )

    before_target_removal = len(
        quality_df
    )

    quality_df = (
        quality_df
        .dropna(
            subset=TARGET_COLUMNS
        )
        .reset_index(drop=True)
    )

    removed_rows = (
        before_target_removal
        - len(quality_df)
    )

    print(
        f"\nRows removed because one or "
        f"more targets were missing: "
        f"{removed_rows:,}"
    )

    # ========================================================
    # NUMERICAL BASE FEATURES
    # ========================================================

    numerical_base_features = [
        "quantity_kg",
        "moisture_percentage",
        "foreign_matter_percentage",
        "damaged_percentage",
        "discolored_percentage",
        "insect_damage_percentage",
        "grain_size",
        "weight_uniformity_percentage",
        "storage_days",
        "storage_temperature_c",
        "storage_humidity_percentage",
    ]

    for column in numerical_base_features:

        quality_df[column] = pd.to_numeric(
            quality_df[column],
            errors="coerce"
        )

    # ========================================================
    # ENGINEERED FEATURES
    # ========================================================

    quality_df["total_damage_percentage"] = (
        quality_df["damaged_percentage"]
        +
        quality_df["discolored_percentage"]
        +
        quality_df["insect_damage_percentage"]
    )

    quality_df["storage_condition_index"] = (
        (
            quality_df["storage_temperature_c"]
            +
            quality_df["storage_humidity_percentage"]
        )
        / 2.0
    )

    quality_df["moisture_storage_exposure"] = (
        quality_df["moisture_percentage"]
        *
        quality_df["storage_days"]
    )

    # ========================================================
    # CLEAN NUMERICAL VALUES
    # ========================================================

    quality_df = quality_df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    numerical_features = (
        numerical_base_features
        + [
            "total_damage_percentage",
            "storage_condition_index",
            "moisture_storage_exposure",
        ]
    )

    quality_df[
        numerical_features
    ] = (
        quality_df[
            numerical_features
        ]
        .fillna(0)
    )

    # ========================================================
    # CATEGORICAL FEATURES
    # ========================================================

    categorical_features = [
        "crop"
    ]

    for column in categorical_features:

        quality_df[column] = (
            quality_df[column]
            .astype("string")
            .fillna("UNKNOWN")
            .str.strip()
        )

    # ========================================================
    # FEATURE COLUMNS
    # ========================================================

    feature_columns = (
        numerical_features
        + categorical_features
    )

    # ========================================================
    # INVALID VALUE CHECK
    # ========================================================

    print(
        "\nChecking feature values..."
    )

    invalid_numerical_values = (
        quality_df[
            numerical_features
        ]
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
        .isna()
        .sum()
        .sum()
    )

    print(
        f"Invalid numerical values: "
        f"{invalid_numerical_values:,}"
    )

    if invalid_numerical_values > 0:

        raise ValueError(
            "Invalid numerical values "
            "found in quality features."
        )

    # ========================================================
    # QUALITY SCORE INFORMATION
    # ========================================================

    print("\nQuality Score:")
    print("-" * 70)

    print(
        f"Minimum: "
        f"{quality_df['quality_score'].min():.2f}"
    )

    print(
        f"Maximum: "
        f"{quality_df['quality_score'].max():.2f}"
    )

    print(
        f"Mean: "
        f"{quality_df['quality_score'].mean():.2f}"
    )

    # ========================================================
    # QUALITY GRADE DISTRIBUTION
    # ========================================================

    print("\nQuality Grade Distribution:")
    print("-" * 70)

    print(
        quality_df[
            "quality_grade"
        ]
        .value_counts()
        .to_string()
    )

    # ========================================================
    # SPOILAGE SCORE INFORMATION
    # ========================================================

    print("\nSpoilage Risk Score:")
    print("-" * 70)

    print(
        f"Minimum: "
        f"{quality_df['spoilage_risk_score'].min():.2f}"
    )

    print(
        f"Maximum: "
        f"{quality_df['spoilage_risk_score'].max():.2f}"
    )

    print(
        f"Mean: "
        f"{quality_df['spoilage_risk_score'].mean():.2f}"
    )

    # ========================================================
    # SPOILAGE RISK DISTRIBUTION
    # ========================================================

    print("\nSpoilage Risk Distribution:")
    print("-" * 70)

    print(
        quality_df[
            "spoilage_risk"
        ]
        .value_counts()
        .to_string()
    )

    # ========================================================
    # EXCLUDED COLUMNS
    # ========================================================

    print(
        "\nExcluded from ML features:"
    )

    print("-" * 70)

    for column in EXCLUDED_COLUMNS:

        if column in quality_df.columns:

            print(
                f"  - {column}"
            )

    # ========================================================
    # NUMERICAL FEATURES
    # ========================================================

    print(
        "\nNumerical feature columns:"
    )

    for column in numerical_features:

        print(
            f"  - {column}"
        )

    # ========================================================
    # CATEGORICAL FEATURES
    # ========================================================

    print(
        "\nCategorical feature columns:"
    )

    for column in categorical_features:

        print(
            f"  - {column}"
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
        f"{quality_df.shape}"
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "QUALITY FEATURE ENGINEERING COMPLETED"
    )

    print(
        "=" * 70
    )

    return (
        quality_df,
        feature_columns,
        TARGET_COLUMNS
    )


# ============================================================
# SAVE QUALITY FEATURES
# ============================================================

def save_quality_features(
    quality_df,
    feature_columns,
    target_columns
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    quality_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "QUALITY FEATURE DATASET SAVED"
    )

    print(
        "=" * 70
    )

    print("\nSaved to:")
    print(OUTPUT_FILE)

    print(
        f"Rows    : "
        f"{len(quality_df):,}"
    )

    print(
        f"Columns : "
        f"{len(quality_df.columns)}"
    )

    print(
        f"Features: "
        f"{len(feature_columns)}"
    )

    print("\nTargets:")

    for target in target_columns:

        print(
            f"  - {target}"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        (
            quality_df,
            feature_columns,
            target_columns
        ) = create_quality_features()

        save_quality_features(
            quality_df,
            feature_columns,
            target_columns
        )

        print(
            "\n✓ Quality feature engineering "
            "completed successfully."
        )

    except Exception as error:

        print(
            "\n" + "=" * 70
        )

        print(
            "QUALITY FEATURE ENGINEERING FAILED"
        )

        print(
            "=" * 70
        )

        print(
            f"\nError: {error}"
        )

        sys.exit(1)