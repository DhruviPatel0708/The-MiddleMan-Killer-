"""
Transaction Risk Model Evaluation

Evaluates:
    payment_status
    delivery_status
"""

import sys
from pathlib import Path

from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.ml.datasets.transaction_dataset import (
    prepare_transaction_dataset
)

from backend.ml.training.base_trainer import (
    load_model
)

from backend.ml.evaluation.metrics import (
    evaluate_classification
)


RANDOM_STATE = 42
TEST_SIZE = 0.20


def evaluate_risk_models():

    print("=" * 70)
    print("RISK PREDICTION MODEL EVALUATION")
    print("=" * 70)

    dataset = prepare_transaction_dataset()

    X = dataset["X"]
    targets = dataset["targets"]

    # --------------------------------------------------------
    # SAME STRATIFIED SPLIT USED FOR TRAINING
    # --------------------------------------------------------

    train_indices, test_indices = train_test_split(
        range(len(X)),
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=targets["payment_status"]
    )

    test_indices = list(test_indices)

    X_test = (
        X.iloc[test_indices]
        .reset_index(drop=True)
    )

    print("\nTest dataset:")
    print(
        f"X_test: {X_test.shape}"
    )

    results = {}

    # ========================================================
    # PAYMENT STATUS
    # ========================================================

    print("\n" + "=" * 70)
    print("1. PAYMENT RISK")
    print("=" * 70)

    payment_model = load_model(
        "payment_risk_model.joblib"
    )

    y_payment = (
        targets["payment_status"]
        .iloc[test_indices]
        .reset_index(drop=True)
    )

    payment_pred = payment_model.predict(
        X_test
    )

    results["payment_status"] = (
        evaluate_classification(
            y_payment,
            payment_pred
        )
    )

    # ========================================================
    # DELIVERY STATUS
    # ========================================================

    print("\n" + "=" * 70)
    print("2. DELIVERY RISK")
    print("=" * 70)

    delivery_model = load_model(
        "delivery_risk_model.joblib"
    )

    y_delivery = (
        targets["delivery_status"]
        .iloc[test_indices]
        .reset_index(drop=True)
    )

    delivery_pred = delivery_model.predict(
        X_test
    )

    results["delivery_status"] = (
        evaluate_classification(
            y_delivery,
            delivery_pred
        )
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("RISK EVALUATION SUMMARY")
    print("=" * 70)

    print("\nPayment Risk:")

    print(
        f"  Accuracy  : "
        f"{results['payment_status']['Accuracy']:.4f}"
    )

    print(
        f"  Precision : "
        f"{results['payment_status']['Precision']:.4f}"
    )

    print(
        f"  Recall    : "
        f"{results['payment_status']['Recall']:.4f}"
    )

    print(
        f"  F1        : "
        f"{results['payment_status']['F1']:.4f}"
    )

    print("\nDelivery Risk:")

    print(
        f"  Accuracy  : "
        f"{results['delivery_status']['Accuracy']:.4f}"
    )

    print(
        f"  Precision : "
        f"{results['delivery_status']['Precision']:.4f}"
    )

    print(
        f"  Recall    : "
        f"{results['delivery_status']['Recall']:.4f}"
    )

    print(
        f"  F1        : "
        f"{results['delivery_status']['F1']:.4f}"
    )

    print("\n" + "=" * 70)
    print("RISK MODEL EVALUATION COMPLETED")
    print("=" * 70)

    return results


if __name__ == "__main__":

    try:

        evaluate_risk_models()

        print(
            "\n✓ Risk model evaluation completed successfully."
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("RISK MODEL EVALUATION FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        sys.exit(1)