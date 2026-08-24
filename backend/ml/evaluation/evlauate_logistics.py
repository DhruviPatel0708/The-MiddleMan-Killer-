"""
Logistics Model Evaluation

Evaluates three separate regression models:

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


# ============================================================
# MAIN EVALUATION FUNCTION
# ============================================================

def evaluate_logistics_models():

    print("=" * 70)
    print("LOGISTICS MODEL EVALUATION")
    print("=" * 70)

    # ========================================================
    # LOAD DATASET
    # ========================================================

    print("\nLoading logistics ML dataset...")

    dataset = prepare_logistics_dataset()

    X = dataset["X"]

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

    indices = list(range(len(X)))

    train_indices, test_indices = train_test_split(
        indices,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE
    )

    X_test = (
        X.iloc[test_indices]
        .reset_index(drop=True)
    )

    print("\nTest dataset:")

    print(
        f"X_test: {X_test.shape}"
    )

    # ========================================================
    # MODEL FILES
    # ========================================================

    model_files = {
        "transport_cost":
            "transport_cost_model.joblib",

        "delay_hours":
            "delay_hours_model.joblib",

        "damage_percentage":
            "damage_percentage_model.joblib"
    }

    results = {}

    predictions = {}

    # ========================================================
    # 1. TRANSPORT COST
    # ========================================================

    print("\n" + "=" * 70)
    print("1. TRANSPORT COST")
    print("=" * 70)

    transport_model = load_model(
        model_files["transport_cost"]
    )

    y_test_transport = (
        targets["transport_cost"]
        .iloc[test_indices]
        .reset_index(drop=True)
    )

    print("\nGenerating predictions...")

    transport_pred = (
        transport_model
        .predict(X_test)
    )

    print("Prediction completed.")

    transport_metrics = (
        evaluate_regression(
            y_test_transport,
            transport_pred
        )
    )

    results["transport_cost"] = (
        transport_metrics
    )

    predictions["transport_cost"] = (
        transport_pred
    )

    # ========================================================
    # 2. DELAY HOURS
    # ========================================================

    print("\n" + "=" * 70)
    print("2. DELAY HOURS")
    print("=" * 70)

    delay_model = load_model(
        model_files["delay_hours"]
    )

    y_test_delay = (
        targets["delay_hours"]
        .iloc[test_indices]
        .reset_index(drop=True)
    )

    print("\nGenerating predictions...")

    delay_pred = (
        delay_model
        .predict(X_test)
    )

    print("Prediction completed.")

    delay_metrics = (
        evaluate_regression(
            y_test_delay,
            delay_pred
        )
    )

    results["delay_hours"] = (
        delay_metrics
    )

    predictions["delay_hours"] = (
        delay_pred
    )

    # ========================================================
    # 3. DAMAGE PERCENTAGE
    # ========================================================

    print("\n" + "=" * 70)
    print("3. DAMAGE PERCENTAGE")
    print("=" * 70)

    damage_model = load_model(
        model_files["damage_percentage"]
    )

    y_test_damage = (
        targets["damage_percentage"]
        .iloc[test_indices]
        .reset_index(drop=True)
    )

    print("\nGenerating predictions...")

    damage_pred = (
        damage_model
        .predict(X_test)
    )

    print("Prediction completed.")

    damage_metrics = (
        evaluate_regression(
            y_test_damage,
            damage_pred
        )
    )

    results["damage_percentage"] = (
        damage_metrics
    )

    predictions["damage_percentage"] = (
        damage_pred
    )

    # ========================================================
    # SAMPLE PREDICTIONS
    # ========================================================

    print("\n" + "=" * 70)
    print("SAMPLE PREDICTIONS")
    print("=" * 70)

    sample_count = min(
        10,
        len(X_test)
    )

    print("\nTransport Cost:")

    for actual, predicted in zip(
        y_test_transport.iloc[:sample_count],
        transport_pred[:sample_count]
    ):
        print(
            f"Actual: {actual:10.2f} | "
            f"Predicted: {predicted:10.2f}"
        )

    print("\nDelay Hours:")

    for actual, predicted in zip(
        y_test_delay.iloc[:sample_count],
        delay_pred[:sample_count]
    ):
        print(
            f"Actual: {actual:8.2f} | "
            f"Predicted: {predicted:8.2f}"
        )

    print("\nDamage Percentage:")

    for actual, predicted in zip(
        y_test_damage.iloc[:sample_count],
        damage_pred[:sample_count]
    ):
        print(
            f"Actual: {actual:8.2f} | "
            f"Predicted: {predicted:8.2f}"
        )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("LOGISTICS EVALUATION SUMMARY")
    print("=" * 70)

    print("\nTransport Cost:")

    print(
        f"  MAE  : "
        f"{results['transport_cost']['MAE']:.4f}"
    )

    print(
        f"  RMSE : "
        f"{results['transport_cost']['RMSE']:.4f}"
    )

    print(
        f"  R²   : "
        f"{results['transport_cost']['R2']:.4f}"
    )

    print("\nDelay Hours:")

    print(
        f"  MAE  : "
        f"{results['delay_hours']['MAE']:.4f}"
    )

    print(
        f"  RMSE : "
        f"{results['delay_hours']['RMSE']:.4f}"
    )

    print(
        f"  R²   : "
        f"{results['delay_hours']['R2']:.4f}"
    )

    print("\nDamage Percentage:")

    print(
        f"  MAE  : "
        f"{results['damage_percentage']['MAE']:.4f}"
    )

    print(
        f"  RMSE : "
        f"{results['damage_percentage']['RMSE']:.4f}"
    )

    print(
        f"  R²   : "
        f"{results['damage_percentage']['R2']:.4f}"
    )

    print("\n" + "=" * 70)
    print("LOGISTICS EVALUATION COMPLETED")
    print("=" * 70)

    return results


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        evaluate_logistics_models()

        print(
            "\n✓ Logistics model evaluation "
            "completed successfully."
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("LOGISTICS MODEL EVALUATION FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        sys.exit(1)