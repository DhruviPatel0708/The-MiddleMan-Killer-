"""
Logistics Model Training

Three separate regression models:

1. transport_cost
2. delay_hours
3. damage_percentage
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

from backend.ml.datasets.logistics_dataset import (
    prepare_logistics_dataset
)

from backend.ml.models.logistics_model import (
    create_transport_cost_model,
    create_delay_hours_model,
    create_damage_percentage_model
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
# TRAIN LOGISTICS MODELS
# ============================================================

def train_logistics_models():

    print("=" * 70)
    print("LOGISTICS MODEL TRAINING")
    print("=" * 70)

    # ========================================================
    # LOAD DATASET
    # ========================================================

    print("\nLoading logistics ML dataset...")

    dataset = prepare_logistics_dataset()

    X = dataset["X"]

    numerical_features = (
        dataset["numerical_columns"]
    )

    categorical_features = (
        dataset["categorical_columns"]
    )

    targets = dataset["targets"]

    required_targets = [
        "transport_cost",
        "delay_hours",
        "damage_percentage"
    ]

    missing_targets = [
        target
        for target in required_targets
        if target not in targets
    ]

    if missing_targets:
        raise ValueError(
            "Missing logistics targets: "
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
    print("CREATING LOGISTICS MODELS")
    print("=" * 70)

    models = {
        "transport_cost":
            create_transport_cost_model(
                numerical_features,
                categorical_features
            ),

        "delay_hours":
            create_delay_hours_model(
                numerical_features,
                categorical_features
            ),

        "damage_percentage":
            create_damage_percentage_model(
                numerical_features,
                categorical_features
            )
    }

    trained_models = {}

    # ========================================================
    # TRAIN EACH MODEL
    # ========================================================

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

        trained_models[target_name] = model

    # ========================================================
    # SAVE MODELS
    # ========================================================

    print("\n" + "=" * 70)
    print("SAVING LOGISTICS MODELS")
    print("=" * 70)

    model_files = {
        "transport_cost":
            "transport_cost_model.joblib",

        "delay_hours":
            "delay_hours_model.joblib",

        "damage_percentage":
            "damage_percentage_model.joblib"
    }

    saved_paths = {}

    for target_name, model in trained_models.items():

        saved_paths[target_name] = save_model(
            model,
            model_files[target_name]
        )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("LOGISTICS TRAINING COMPLETED")
    print("=" * 70)

    print("\nTrained models:")

    for target_name in trained_models:
        print(
            f"  ✓ {target_name}"
        )

    print("\nSaved models:")

    for target_name, path in saved_paths.items():

        print(
            f"\n{target_name}:"
        )

        print(
            f"  {path}"
        )

    print("\n" + "=" * 70)

    return trained_models


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        train_logistics_models()

        print(
            "\n✓ Logistics model training "
            "completed successfully."
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("LOGISTICS MODEL TRAINING FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        sys.exit(1)