"""
Crop Quality Model Evaluation

Evaluates four separate models:

1. quality_score
2. quality_grade
3. spoilage_risk_score
4. spoilage_risk
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

from backend.ml.datasets.quality_dataset import (
    prepare_quality_dataset
)

from backend.ml.training.base_trainer import (
    load_model
)

from backend.ml.evaluation.metrics import (
    evaluate_regression,
    evaluate_classification
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42
TEST_SIZE = 0.20


# ============================================================
# MAIN EVALUATION FUNCTION
# ============================================================

def evaluate_quality_models():

    print("=" * 70)
    print("CROP QUALITY MODEL EVALUATION")
    print("=" * 70)

    # ========================================================
    # LOAD DATASET
    # ========================================================

    print("\nLoading quality ML dataset...")

    dataset = prepare_quality_dataset()

    X = dataset["X"]

    numerical_features = (
        dataset["numerical_columns"]
    )

    categorical_features = (
        dataset["categorical_columns"]
    )

    # ========================================================
    # TARGETS
    # ========================================================

    targets = dataset["targets"]

    required_targets = [
        "quality_score",
        "quality_grade",
        "spoilage_risk_score",
        "spoilage_risk"
    ]

    missing_targets = [
        target
        for target in required_targets
        if target not in targets
    ]

    if missing_targets:
        raise ValueError(
            "Missing quality targets: "
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
    # TARGET TEST SETS
    # ========================================================

    y_test = {}

    for target_name in required_targets:

        y_test[target_name] = (
            targets[target_name]
            .iloc[test_indices]
            .reset_index(drop=True)
        )

        print(
            f"{target_name}: "
            f"{y_test[target_name].shape}"
        )

    # ========================================================
    # MODEL FILES
    # ========================================================

    model_files = {
        "quality_score":
            "quality_score_model.joblib",

        "quality_grade":
            "quality_grade_model.joblib",

        "spoilage_risk_score":
            "spoilage_risk_score_model.joblib",

        "spoilage_risk":
            "spoilage_risk_model.joblib",
    }

    # ========================================================
    # RESULTS
    # ========================================================

    results = {}

    # ========================================================
    # 1. QUALITY SCORE
    # ========================================================

    print("\n" + "=" * 70)
    print("1. QUALITY SCORE")
    print("=" * 70)

    quality_score_model = load_model(
        model_files["quality_score"]
    )

    quality_score_pred = (
        quality_score_model.predict(
            X_test
        )
    )

    quality_score_metrics = (
        evaluate_regression(
            y_test["quality_score"],
            quality_score_pred
        )
    )

    results["quality_score"] = (
        quality_score_metrics
    )

    # ========================================================
    # 2. QUALITY GRADE
    # ========================================================

    print("\n" + "=" * 70)
    print("2. QUALITY GRADE")
    print("=" * 70)

    quality_grade_model = load_model(
        model_files["quality_grade"]
    )

    quality_grade_pred = (
        quality_grade_model.predict(
            X_test
        )
    )

    quality_grade_metrics = (
        evaluate_classification(
            y_test["quality_grade"],
            quality_grade_pred
        )
    )

    results["quality_grade"] = (
        quality_grade_metrics
    )

    # ========================================================
    # 3. SPOILAGE RISK SCORE
    # ========================================================

    print("\n" + "=" * 70)
    print("3. SPOILAGE RISK SCORE")
    print("=" * 70)

    spoilage_risk_score_model = load_model(
        model_files["spoilage_risk_score"]
    )

    spoilage_risk_score_pred = (
        spoilage_risk_score_model.predict(
            X_test
        )
    )

    spoilage_risk_score_metrics = (
        evaluate_regression(
            y_test["spoilage_risk_score"],
            spoilage_risk_score_pred
        )
    )

    results["spoilage_risk_score"] = (
        spoilage_risk_score_metrics
    )

    # ========================================================
    # 4. SPOILAGE RISK
    # ========================================================

    print("\n" + "=" * 70)
    print("4. SPOILAGE RISK")
    print("=" * 70)

    spoilage_risk_model = load_model(
        model_files["spoilage_risk"]
    )

    spoilage_risk_pred = (
        spoilage_risk_model.predict(
            X_test
        )
    )

    spoilage_risk_metrics = (
        evaluate_classification(
            y_test["spoilage_risk"],
            spoilage_risk_pred
        )
    )

    results["spoilage_risk"] = (
        spoilage_risk_metrics
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

    print("\nQuality Score:")

    for actual, predicted in zip(
        y_test["quality_score"].iloc[:sample_count],
        quality_score_pred[:sample_count]
    ):
        print(
            f"Actual: {actual:8.2f} | "
            f"Predicted: {predicted:8.2f}"
        )

    print("\nQuality Grade:")

    for actual, predicted in zip(
        y_test["quality_grade"].iloc[:sample_count],
        quality_grade_pred[:sample_count]
    ):
        print(
            f"Actual: {actual:<10} | "
            f"Predicted: {predicted}"
        )

    print("\nSpoilage Risk Score:")

    for actual, predicted in zip(
        y_test["spoilage_risk_score"].iloc[:sample_count],
        spoilage_risk_score_pred[:sample_count]
    ):
        print(
            f"Actual: {actual:8.2f} | "
            f"Predicted: {predicted:8.2f}"
        )

    print("\nSpoilage Risk:")

    for actual, predicted in zip(
        y_test["spoilage_risk"].iloc[:sample_count],
        spoilage_risk_pred[:sample_count]
    ):
        print(
            f"Actual: {actual:<10} | "
            f"Predicted: {predicted}"
        )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("CROP QUALITY EVALUATION SUMMARY")
    print("=" * 70)

    print("\nREGRESSION MODELS")

    print(
        f"\nQuality Score:"
        f"\n  MAE  : {results['quality_score']['MAE']:.4f}"
        f"\n  RMSE : {results['quality_score']['RMSE']:.4f}"
        f"\n  R²   : {results['quality_score']['R2']:.4f}"
    )

    print(
        f"\nSpoilage Risk Score:"
        f"\n  MAE  : {results['spoilage_risk_score']['MAE']:.4f}"
        f"\n  RMSE : {results['spoilage_risk_score']['RMSE']:.4f}"
        f"\n  R²   : {results['spoilage_risk_score']['R2']:.4f}"
    )

    print("\nCLASSIFICATION MODELS")

    print(
        f"\nQuality Grade:"
        f"\n  Accuracy  : {results['quality_grade']['Accuracy']:.4f}"
        f"\n  Precision : {results['quality_grade']['Precision']:.4f}"
        f"\n  Recall    : {results['quality_grade']['Recall']:.4f}"
        f"\n  F1        : {results['quality_grade']['F1']:.4f}"
    )

    print(
        f"\nSpoilage Risk:"
        f"\n  Accuracy  : {results['spoilage_risk']['Accuracy']:.4f}"
        f"\n  Precision : {results['spoilage_risk']['Precision']:.4f}"
        f"\n  Recall    : {results['spoilage_risk']['Recall']:.4f}"
        f"\n  F1        : {results['spoilage_risk']['F1']:.4f}"
    )

    print("\n" + "=" * 70)
    print("CROP QUALITY EVALUATION COMPLETED")
    print("=" * 70)

    return results


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        evaluate_quality_models()

        print(
            "\n✓ Crop quality model evaluation "
            "completed successfully."
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("CROP QUALITY MODEL EVALUATION FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        sys.exit(1)