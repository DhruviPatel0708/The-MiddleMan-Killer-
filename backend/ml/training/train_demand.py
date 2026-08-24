"""
Demand Forecasting Model Training

Target:
    next_day_demand_tonnes

Model:
    Random Forest Regression

Input:
    data/processed/demand_features.csv

Output:
    backend/ml/saved_models/demand_model.joblib
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

from backend.ml.datasets.demand_dataset import (
    prepare_demand_dataset
)

from backend.ml.models.demand_model import (
    create_demand_model
)

from backend.ml.training.base_trainer import (
    save_model
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42
TEST_SIZE = 0.20

TARGET_COLUMN = (
    "next_day_demand_tonnes"
)


# ============================================================
# MAIN TRAINING FUNCTION
# ============================================================

def train_demand_model():

    print("=" * 70)
    print("DEMAND FORECASTING MODEL TRAINING")
    print("=" * 70)

    # ========================================================
    # LOAD PREPARED DATASET
    # ========================================================

    print("\nLoading demand ML dataset...")

    dataset = prepare_demand_dataset()

    X = dataset["X"]
    y = dataset["y"]

    numerical_features = (
        dataset["numerical_columns"]
    )

    categorical_features = (
        dataset["categorical_columns"]
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

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE
        )
    )

    print("\nTraining:")

    print(
        f"X_train: {X_train.shape}"
    )

    print(
        f"y_train: {y_train.shape}"
    )

    print("\nTesting:")

    print(
        f"X_test : {X_test.shape}"
    )

    print(
        f"y_test : {y_test.shape}"
    )

    # ========================================================
    # CREATE MODEL
    # ========================================================

    print("\n" + "=" * 70)
    print("CREATING DEMAND MODEL")
    print("=" * 70)

    model = create_demand_model(
        numerical_features=numerical_features,
        categorical_features=categorical_features
    )

    print("\nModel:")

    print(
        model
    )

    # ========================================================
    # TRAIN MODEL
    # ========================================================

    print("\n" + "=" * 70)
    print("TRAINING DEMAND MODEL")
    print("=" * 70)

    print("\nTraining started...")
    print("Please wait.")

    model.fit(
        X_train,
        y_train
    )

    print(
        "\nDemand model training completed."
    )

    # ========================================================
    # SAVE MODEL
    # ========================================================

    print("\n" + "=" * 70)
    print("SAVING DEMAND MODEL")
    print("=" * 70)

    model_path = save_model(
        model,
        "demand_model.joblib"
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("DEMAND MODEL TRAINING COMPLETED")
    print("=" * 70)

    print(
        "\nTarget:"
    )

    print(
        f"  {TARGET_COLUMN}"
    )

    print(
        "\nTraining rows:"
    )

    print(
        f"  {len(X_train):,}"
    )

    print(
        "\nTesting rows:"
    )

    print(
        f"  {len(X_test):,}"
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

        train_demand_model()

        print(
            "\n✓ Demand model training completed successfully."
        )

    except Exception as e:

        print("\n" + "=" * 70)
        print("DEMAND MODEL TRAINING FAILED")
        print("=" * 70)

        print(
            f"\nError: {e}"
        )

        sys.exit(1)