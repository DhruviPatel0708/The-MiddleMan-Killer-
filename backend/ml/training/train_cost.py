"""
Cost Estimation Model Training

Target:
    estimated_total_cost
"""

import sys
from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

from backend.ml.datasets.cost_dataset import (
    prepare_cost_dataset
)

from backend.ml.models.cost_model import (
    create_cost_model
)

from backend.ml.training.base_trainer import (
    save_model
)


# ============================================================
# TRAIN COST MODEL
# ============================================================

def train_cost_model():

    print("=" * 70)
    print("COST ESTIMATION MODEL TRAINING")
    print("=" * 70)

    # ========================================================
    # LOAD DATASET
    # ========================================================

    print("\nLoading cost ML dataset...")

    dataset = prepare_cost_dataset()

    X_train = dataset["X_train"]
    y_train = dataset["y_train"]

    numerical_features = (
        dataset["numerical_columns"]
    )

    categorical_features = (
        dataset["categorical_columns"]
    )

    print("\nDataset ready for training.")

    print(
        f"Training rows : {len(X_train):,}"
    )

    print(
        f"Features      : {X_train.shape[1]}"
    )

    # ========================================================
    # CREATE MODEL
    # ========================================================

    print("\n" + "=" * 70)
    print("CREATING COST ESTIMATION MODEL")
    print("=" * 70)

    model = create_cost_model(
        numerical_features,
        categorical_features
    )

    print("\nModel:")
    print(model)

    # ========================================================
    # TRAIN
    # ========================================================

    print("\n" + "=" * 70)
    print("TRAINING COST ESTIMATION MODEL")
    print("=" * 70)

    print("\nTraining started...")
    print("Please wait.")

    model.fit(
        X_train,
        y_train
    )

    print(
        "\nCost estimation model training completed."
    )

    # ========================================================
    # SAVE
    # ========================================================

    print("\n" + "=" * 70)
    print("SAVING COST ESTIMATION MODEL")
    print("=" * 70)

    model_path = save_model(
        model,
        "cost_estimation_model.joblib"
    )

    print(
        "\nModel saved successfully:"
    )

    print(
        model_path
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("COST ESTIMATION TRAINING COMPLETED")
    print("=" * 70)

    print(
        "\nTarget:"
    )

    print(
        "  estimated_total_cost"
    )

    print(
        f"\nTraining rows:"
        f"\n  {len(X_train):,}"
    )

    print(
        f"\nFeatures:"
        f"\n  {X_train.shape[1]}"
    )

    print(
        "\nSaved model:"
    )

    print(
        f"  {model_path}"
    )

    print("\n" + "=" * 70)

    return model


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        train_cost_model()

        print(
            "\n✓ Cost estimation model "
            "training completed successfully."
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("COST ESTIMATION MODEL TRAINING FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        sys.exit(1)