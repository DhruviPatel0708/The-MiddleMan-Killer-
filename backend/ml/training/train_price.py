"""
Price Prediction Model Training

Target:
    next_modal_price_per_quintal

Model:
    Random Forest Regression

Input dataset:
    data/processed/price_features.csv

Output:
    backend/ml/saved_models/price_model.joblib
"""

import sys
from pathlib import Path

# Allow imports from backend/ml
PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from sklearn.model_selection import train_test_split

from backend.ml.datasets.price_dataset import (
    prepare_price_dataset
)

from backend.ml.models.price_model import (
    create_price_model
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
    "next_modal_price_per_quintal"
)


# ============================================================
# MAIN TRAINING FUNCTION
# ============================================================

def train_price_model():

    print("=" * 70)
    print("PRICE PREDICTION MODEL TRAINING")
    print("=" * 70)

    # ========================================================
    # LOAD PREPARED DATASET
    # ========================================================

    print("\nLoading price ML dataset...")

    dataset = prepare_price_dataset()

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
    print("CREATING PRICE MODEL")
    print("=" * 70)

    model = create_price_model(
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
    print("TRAINING PRICE MODEL")
    print("=" * 70)

    print("\nTraining started...")
    print("Please wait.")

    model.fit(
        X_train,
        y_train
    )

    print("\nPrice model training completed.")

    # ========================================================
    # SAVE MODEL
    # ========================================================

    print("\n" + "=" * 70)
    print("SAVING PRICE MODEL")
    print("=" * 70)

    model_path = save_model(
        model,
        "price_model.joblib"
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("PRICE MODEL TRAINING COMPLETED")
    print("=" * 70)

    print(
        f"\nTarget:"
    )

    print(
        f"  {TARGET_COLUMN}"
    )

    print(
        f"\nTraining rows:"
    )

    print(
        f"  {len(X_train):,}"
    )

    print(
        f"\nTesting rows:"
    )

    print(
        f"  {len(X_test):,}"
    )

    print(
        f"\nSaved model:"
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

        train_price_model()

        print(
            "\n✓ Price model training completed successfully."
        )

    except Exception as e:

        print("\n" + "=" * 70)
        print("PRICE MODEL TRAINING FAILED")
        print("=" * 70)

        print(
            f"\nError: {e}"
        )

        sys.exit(1)