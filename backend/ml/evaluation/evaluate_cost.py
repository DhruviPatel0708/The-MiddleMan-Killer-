"""
Cost Estimation Model Evaluation

Target:
    estimated_total_cost

Metrics:
    MAE
    RMSE
    R²
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

from backend.ml.training.base_trainer import (
    load_model
)

from backend.ml.evaluation.metrics import (
    evaluate_regression
)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_FILE = "cost_estimation_model.joblib"
TARGET_COLUMN = "estimated_total_cost"


# ============================================================
# EVALUATE COST MODEL
# ============================================================

def evaluate_cost_model():

    print("=" * 70)
    print("COST ESTIMATION MODEL EVALUATION")
    print("=" * 70)

    # ========================================================
    # LOAD DATASET
    # ========================================================

    print("\nLoading cost ML dataset...")

    dataset = prepare_cost_dataset()

    X_test = dataset["X_test"]
    y_test = dataset["y_test"]

    print("\nDataset loaded.")

    print(
        f"Test rows : {len(X_test):,}"
    )

    print(
        f"Features  : {X_test.shape[1]}"
    )

    # ========================================================
    # LOAD MODEL
    # ========================================================

    print("\n" + "=" * 70)
    print("LOADING COST ESTIMATION MODEL")
    print("=" * 70)

    model = load_model(
        MODEL_FILE
    )

    # ========================================================
    # PREDICTIONS
    # ========================================================

    print("\n" + "=" * 70)
    print("GENERATING COST PREDICTIONS")
    print("=" * 70)

    print("\nPrediction started...")

    predictions = model.predict(
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
        predictions
    )

    # ========================================================
    # SAMPLE PREDICTIONS
    # ========================================================

    print("\n" + "=" * 70)
    print("SAMPLE PREDICTIONS")
    print("=" * 70)

    sample_count = min(
        10,
        len(y_test)
    )

    print("\nActual vs Predicted:")

    for actual, predicted in zip(
        y_test.iloc[:sample_count],
        predictions[:sample_count]
    ):

        print(
            f"Actual: {actual:12.2f} | "
            f"Predicted: {predicted:12.2f}"
        )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print("\n" + "=" * 70)
    print("COST ESTIMATION EVALUATION COMPLETED")
    print("=" * 70)

    print(
        f"\nTarget:"
    )

    print(
        f"  {TARGET_COLUMN}"
    )

    print(
        f"\nMAE  : "
        f"{metrics['MAE']:.4f}"
    )

    print(
        f"RMSE : "
        f"{metrics['RMSE']:.4f}"
    )

    print(
        f"R²   : "
        f"{metrics['R2']:.4f}"
    )

    print("\n" + "=" * 70)

    return metrics


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        evaluate_cost_model()

        print(
            "\n✓ Cost estimation model "
            "evaluation completed successfully."
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("COST ESTIMATION EVALUATION FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        sys.exit(1)