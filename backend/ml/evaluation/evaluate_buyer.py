"""
Buyer Reliability Model Evaluation

Target:
    buyer_reliability_label

Metrics:
    Accuracy
    Precision
    Recall
    F1
    Classification Report
    Confusion Matrix

Important:
    The dataset is highly imbalanced, so macro-F1 and
    per-class results are important.
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

from backend.ml.training.base_trainer import (
    load_model
)

from backend.ml.evaluation.metrics import (
    evaluate_classification
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42
TEST_SIZE = 0.20

TARGET_COLUMN = "buyer_reliability_label"


# ============================================================
# BUYER MODEL EVALUATION
# ============================================================

def evaluate_buyer_model():

    print("=" * 70)
    print("BUYER RELIABILITY MODEL EVALUATION")
    print("=" * 70)

    # ========================================================
    # LOAD DATASET
    # ========================================================

    print("\nLoading buyer ML dataset...")

    dataset = prepare_buyer_dataset()

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
    # RECREATE SAME STRATIFIED TEST SPLIT
    # ========================================================

    print("\n" + "=" * 70)
    print("RECREATING TEST SPLIT")
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

    print("\nTest dataset:")

    print(
        f"X_test: {X_test.shape}"
    )

    print(
        f"y_test: {y_test.shape}"
    )

    print("\nTest target distribution:")

    print(
        y_test.value_counts()
        .to_string()
    )

    # ========================================================
    # LOAD MODEL
    # ========================================================

    print("\n" + "=" * 70)
    print("LOADING BUYER MODEL")
    print("=" * 70)

    model = load_model(
        "buyer_model.joblib"
    )

    # ========================================================
    # PREDICTIONS
    # ========================================================

    print("\n" + "=" * 70)
    print("GENERATING BUYER PREDICTIONS")
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

    metrics = evaluate_classification(
        y_test,
        y_pred
    )

    # ========================================================
    # PER-CLASS PREDICTION DISTRIBUTION
    # ========================================================

    print("\n" + "=" * 70)
    print("PREDICTED CLASS DISTRIBUTION")
    print("=" * 70)

    print(
        "\nPredicted classes:"
    )

    print(
        __import__("pandas")
        .Series(y_pred)
        .value_counts()
        .to_string()
    )

    # ========================================================
    # ACTUAL VS PREDICTED SAMPLE
    # ========================================================

    print("\n" + "=" * 70)
    print("SAMPLE PREDICTIONS")
    print("=" * 70)

    sample_count = min(
        20,
        len(y_test)
    )

    print(
        "\nActual vs Predicted:"
    )

    for actual, predicted in zip(
        y_test.iloc[:sample_count],
        y_pred[:sample_count]
    ):

        print(
            f"Actual: {actual:<12} | "
            f"Predicted: {predicted}"
        )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print("\n" + "=" * 70)
    print("BUYER MODEL EVALUATION COMPLETED")
    print("=" * 70)

    print(
        f"\nTarget:"
    )

    print(
        f"  {TARGET_COLUMN}"
    )

    print(
        f"\nAccuracy  : "
        f"{metrics['Accuracy']:.4f}"
    )

    print(
        f"Precision : "
        f"{metrics['Precision']:.4f}"
    )

    print(
        f"Recall    : "
        f"{metrics['Recall']:.4f}"
    )

    print(
        f"F1 Score  : "
        f"{metrics['F1']:.4f}"
    )

    print("\n" + "=" * 70)

    print(
        "\nImportant:"
    )

    print(
        "The UNRELIABLE class contains only "
        "4 original samples."
    )

    print(
        "Therefore, per-class performance for "
        "UNRELIABLE must be interpreted cautiously."
    )

    return metrics


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        evaluate_buyer_model()

        print(
            "\n✓ Buyer model evaluation completed successfully."
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("BUYER MODEL EVALUATION FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        sys.exit(1)