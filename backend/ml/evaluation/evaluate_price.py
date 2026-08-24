"""
Price Prediction Model Evaluation

Loads the trained price model and evaluates it
on the same 20% test split used during training.

Metrics:
    MAE
    RMSE
    R²
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

from backend.ml.datasets.price_dataset import (
    prepare_price_dataset
)

from backend.ml.training.base_trainer import (
    load_model
)

from backend.ml.evaluation.metrics import (
    evaluate_regression
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
# EVALUATE PRICE MODEL
# ============================================================

def evaluate_price_model():

    print("=" * 70)
    print("PRICE PREDICTION MODEL EVALUATION")
    print("=" * 70)

    # ========================================================
    # LOAD DATASET
    # ========================================================

    print("\nLoading price ML dataset...")

    dataset = prepare_price_dataset()

    X = dataset["X"]
    y = dataset["y"]

    print("\nDataset loaded.")

    print(
        f"Rows    : {len(X):,}"
    )

    print(
        f"Features: {X.shape[1]}"
    )

    # ========================================================
    # RECREATE SAME TEST SPLIT
    # ========================================================

    print("\n" + "=" * 70)
    print("RECREATING TEST SPLIT")
    print("=" * 70)

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE
        )
    )

    print("\nTest dataset:")

    print(
        f"X_test: {X_test.shape}"
    )

    print(
        f"y_test: {y_test.shape}"
    )

    # ========================================================
    # LOAD TRAINED MODEL
    # ========================================================

    print("\n" + "=" * 70)
    print("LOADING PRICE MODEL")
    print("=" * 70)

    model = load_model(
        "price_model.joblib"
    )

    # ========================================================
    # PREDICTION
    # ========================================================

    print("\n" + "=" * 70)
    print("GENERATING PRICE PREDICTIONS")
    print("=" * 70)

    print("\nPrediction started...")

    y_pred = model.predict(
        X_test
    )

    print(
        "Prediction completed."
    )

    # ========================================================
    # EVALUATION
    # ========================================================

    metrics = evaluate_regression(
        y_test,
        y_pred
    )

    # ========================================================
    # SAMPLE PREDICTIONS
    # ========================================================

    print("\n" + "=" * 70)
    print("SAMPLE PREDICTIONS")
    print("=" * 70)

    print(
        "\nActual vs Predicted:"
    )

    sample_count = min(
        10,
        len(y_test)
    )

    for actual, predicted in zip(
        y_test.iloc[:sample_count],
        y_pred[:sample_count]
    ):

        print(
            f"Actual: {actual:10.2f} | "
            f"Predicted: {predicted:10.2f}"
        )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print("\n" + "=" * 70)
    print("PRICE MODEL EVALUATION COMPLETED")
    print("=" * 70)

    print(
        f"\nTarget:"
    )

    print(
        f"  {TARGET_COLUMN}"
    )

    print(
        f"\nMAE  : {metrics['MAE']:.4f}"
    )

    print(
        f"RMSE : {metrics['RMSE']:.4f}"
    )

    print(
        f"R²   : {metrics['R2']:.4f}"
    )

    print("\n" + "=" * 70)

    return metrics


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        evaluate_price_model()

        print(
            "\n✓ Price model evaluation "
            "completed successfully."
        )

    except Exception as e:

        print("\n" + "=" * 70)
        print("PRICE MODEL EVALUATION FAILED")
        print("=" * 70)

        print(
            f"\nError: {e}"
        )

        sys.exit(1)