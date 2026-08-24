"""
Buyer Reliability Model Training

Target:
    buyer_reliability_label

Problem:
    Multiclass classification
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

from backend.ml.datasets.buyer_dataset import (
    prepare_buyer_dataset
)

from backend.ml.models.buyer_model import (
    create_buyer_model
)

from backend.ml.training.base_trainer import (
    save_model
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42
TEST_SIZE = 0.20

TARGET_COLUMN = "buyer_reliability_label"


# ============================================================
# TRAIN BUYER MODEL
# ============================================================

def train_buyer_model():

    print("=" * 70)
    print("BUYER RELIABILITY MODEL TRAINING")
    print("=" * 70)

    # ========================================================
    # LOAD DATASET
    # ========================================================

    print("\nLoading buyer ML dataset...")

    dataset = prepare_buyer_dataset()

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
    # STRATIFIED TRAIN / TEST SPLIT
    # ========================================================

    print("\n" + "=" * 70)
    print("CREATING STRATIFIED TRAIN / TEST SPLIT")
    print("=" * 70)

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            stratify=y
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
    # TARGET DISTRIBUTION
    # ========================================================

    print("\nTraining target distribution:")

    print(
        y_train.value_counts()
        .to_string()
    )

    print("\nTesting target distribution:")

    print(
        y_test.value_counts()
        .to_string()
    )

    # ========================================================
    # CREATE MODEL
    # ========================================================

    print("\n" + "=" * 70)
    print("CREATING BUYER RELIABILITY MODEL")
    print("=" * 70)

    model = create_buyer_model(
        numerical_features=numerical_features,
        categorical_features=categorical_features
    )

    print("\nModel:")
    print(model)

    # ========================================================
    # TRAIN
    # ========================================================

    print("\n" + "=" * 70)
    print("TRAINING BUYER RELIABILITY MODEL")
    print("=" * 70)

    print("\nTraining started...")
    print("Please wait.")

    model.fit(
        X_train,
        y_train
    )

    print(
        "\nBuyer reliability model training completed."
    )

    # ========================================================
    # SAVE
    # ========================================================

    print("\n" + "=" * 70)
    print("SAVING BUYER MODEL")
    print("=" * 70)

    model_path = save_model(
        model,
        "buyer_model.joblib"
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("BUYER MODEL TRAINING COMPLETED")
    print("=" * 70)

    print("\nTarget:")

    print(
        f"  {TARGET_COLUMN}"
    )

    print("\nTraining rows:")

    print(
        f"  {len(X_train):,}"
    )

    print("\nTesting rows:")

    print(
        f"  {len(X_test):,}"
    )

    print("\nSaved model:")

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

        train_buyer_model()

        print(
            "\n✓ Buyer model training completed successfully."
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("BUYER MODEL TRAINING FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        sys.exit(1)