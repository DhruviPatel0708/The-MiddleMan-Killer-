"""
Common ML Evaluation Metrics
"""

import numpy as np

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# REGRESSION METRICS
# ============================================================

def evaluate_regression(
    y_true,
    y_pred
):
    """
    Calculate regression metrics.
    """

    mae = mean_absolute_error(
        y_true,
        y_pred
    )

    mse = mean_squared_error(
        y_true,
        y_pred
    )

    rmse = np.sqrt(mse)

    r2 = r2_score(
        y_true,
        y_pred
    )

    metrics = {
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2
    }

    print("\n" + "=" * 70)
    print("REGRESSION EVALUATION")
    print("=" * 70)

    print(
        f"\nMAE  : {mae:.4f}"
    )

    print(
        f"RMSE : {rmse:.4f}"
    )

    print(
        f"R²   : {r2:.4f}"
    )

    return metrics


# ============================================================
# CLASSIFICATION METRICS
# ============================================================

def evaluate_classification(
    y_true,
    y_pred
):
    """
    Calculate classification metrics.
    """

    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    precision = precision_score(
        y_true,
        y_pred,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_pred,
        average="weighted",
        zero_division=0
    )

    metrics = {
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1
    }

    print("\n" + "=" * 70)
    print("CLASSIFICATION EVALUATION")
    print("=" * 70)

    print(
        f"\nAccuracy  : {accuracy:.4f}"
    )

    print(
        f"Precision : {precision:.4f}"
    )

    print(
        f"Recall    : {recall:.4f}"
    )

    print(
        f"F1 Score  : {f1:.4f}"
    )

    print("\nClassification Report:")
    print(
        classification_report(
            y_true,
            y_pred,
            zero_division=0
        )
    )

    print("Confusion Matrix:")
    print(
        confusion_matrix(
            y_true,
            y_pred
        )
    )

    return metrics