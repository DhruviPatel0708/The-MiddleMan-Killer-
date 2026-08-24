"""
Crop Quality Model Training

Four separate models:

1. quality_score
2. quality_grade
3. spoilage_risk_score
4. spoilage_risk
"""

import sys
from pathlib import Path

from sklearn.model_selection import train_test_split


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

from backend.ml.datasets.quality_dataset import (
    prepare_quality_dataset
)

from backend.ml.models.quality_model import (
    create_quality_score_model,
    create_quality_grade_model,
    create_spoilage_risk_score_model,
    create_spoilage_risk_model
)

from backend.ml.training.base_trainer import (
    save_model
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42
TEST_SIZE = 0.20


# ============================================================
# TRAIN QUALITY MODELS
# ============================================================

def train_quality_models():

    print("=" * 70)
    print("CROP QUALITY MODEL TRAINING")
    print("=" * 70)

    # ========================================================
    # LOAD QUALITY DATASET
    # ========================================================

    print("\nLoading quality ML dataset...")

    dataset = prepare_quality_dataset()

    X = dataset["X"]

    numerical_features = (
        dataset["numerical_columns"]
    )

    categorical_features = (
        dataset["categorical_columns"]
    )

    # ========================================================
    # IMPORTANT:
    # QUALITY DATASET RETURNS TARGETS AS A DICTIONARY
    # ========================================================

    targets = dataset["targets"]

    required_targets = [
        "quality_score",
        "quality_grade",
        "spoilage_risk_score",
        "spoilage_risk"
    ]

    missing_targets = [
        target
        for target in required_targets
        if target not in targets
    ]

    if missing_targets:

        raise ValueError(
            "Missing quality targets: "
            f"{missing_targets}"
        )

    print("\nDataset ready for training.")

    print(
        f"Rows    : {len(X):,}"
    )

    print(
        f"Features: {X.shape[1]}"
    )

    # ========================================================
    # TRAIN / TEST SPLIT
    # ========================================================

    print("\n" + "=" * 70)
    print("CREATING TRAIN / TEST SPLIT")
    print("=" * 70)

    train_indices, test_indices = train_test_split(
        range(len(X)),
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE
    )

    train_indices = list(train_indices)
    test_indices = list(test_indices)

    X_train = (
        X.iloc[train_indices]
        .reset_index(drop=True)
    )

    X_test = (
        X.iloc[test_indices]
        .reset_index(drop=True)
    )

    print("\nTraining:")
    print(
        f"X_train: {X_train.shape}"
    )

    print("\nTesting:")
    print(
        f"X_test : {X_test.shape}"
    )

    # ========================================================
    # CREATE MODELS
    # ========================================================

    print("\n" + "=" * 70)
    print("CREATING QUALITY MODELS")
    print("=" * 70)

    models = {

        "quality_score":
            create_quality_score_model(
                numerical_features,
                categorical_features
            ),

        "quality_grade":
            create_quality_grade_model(
                numerical_features,
                categorical_features
            ),

        "spoilage_risk_score":
            create_spoilage_risk_score_model(
                numerical_features,
                categorical_features
            ),

        "spoilage_risk":
            create_spoilage_risk_model(
                numerical_features,
                categorical_features
            ),
    }

    # ========================================================
    # TRAIN MODELS
    # ========================================================

    trained_models = {}

    for target_name, model in models.items():

        print("\n" + "=" * 70)
        print(
            f"TRAINING: {target_name}"
        )
        print("=" * 70)

        y = targets[target_name]

        y_train = (
            y.iloc[train_indices]
            .reset_index(drop=True)
        )

        print(
            f"\nTraining samples: "
            f"{len(y_train):,}"
        )

        # Classification distribution
        if target_name in [
            "quality_grade",
            "spoilage_risk"
        ]:

            print(
                "\nTarget distribution:"
            )

            print(
                y_train
                .value_counts()
                .to_string()
            )

        print(
            "\nTraining started..."
        )

        model.fit(
            X_train,
            y_train
        )

        print(
            f"{target_name} "
            "training completed."
        )

        trained_models[
            target_name
        ] = model

    # ========================================================
    # SAVE MODELS
    # ========================================================

    print("\n" + "=" * 70)
    print("SAVING QUALITY MODELS")
    print("=" * 70)

    model_files = {

        "quality_score":
            "quality_score_model.joblib",

        "quality_grade":
            "quality_grade_model.joblib",

        "spoilage_risk_score":
            "spoilage_risk_score_model.joblib",

        "spoilage_risk":
            "spoilage_risk_model.joblib",
    }

    saved_paths = {}

    for target_name, model in trained_models.items():

        saved_paths[
            target_name
        ] = save_model(
            model,
            model_files[target_name]
        )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("CROP QUALITY TRAINING COMPLETED")
    print("=" * 70)

    print("\nTrained models:")

    for target_name in trained_models:

        print(
            f"  ✓ {target_name}"
        )

    print("\nSaved models:")

    for target_name, model_path in saved_paths.items():

        print(
            f"\n{target_name}:"
        )

        print(
            f"  {model_path}"
        )

    print("\n" + "=" * 70)

    return trained_models


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        train_quality_models()

        print(
            "\n✓ Crop quality model training "
            "completed successfully."
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("CROP QUALITY MODEL TRAINING FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        sys.exit(1)