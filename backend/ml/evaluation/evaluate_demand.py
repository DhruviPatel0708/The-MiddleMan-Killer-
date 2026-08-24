"""
ALL AGRICULTURE AI MODELS - INTEGRATION TEST

Tests every saved ML model by:
1. Loading the model
2. Loading its feature dataset
3. Selecting the exact features expected by the model
4. Generating predictions
5. Checking prediction length
6. Checking NaN / Inf values
7. Checking that predictions are not constant/broken
8. Printing a final PASS/FAIL summary

This script DOES NOT retrain any model.
It DOES NOT modify any dataset.
It DOES NOT modify any saved model.
"""

from pathlib import Path
import warnings

import joblib
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


# ======================================================================
# PATHS
# ======================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "backend" / "ml" / "saved_models"


print("=" * 70)
print("AGRICULTURE AI - COMPLETE MODEL TEST")
print("=" * 70)

print(f"\nProject root:")
print(PROJECT_ROOT)

print(f"\nData directory:")
print(DATA_DIR)

print(f"\nSaved models directory:")
print(MODEL_DIR)


# ======================================================================
# MODEL CONFIGURATION
# ======================================================================

MODEL_CONFIG = {

    # --------------------------------------------------------------
    # PRICE
    # --------------------------------------------------------------
    "Price Prediction": {
        "model_candidates": [
            "price_model.joblib",
            "price_prediction_model.joblib",
        ],
        "data_candidates": [
            "price_features.csv",
            "price_dataset.csv",
        ],
    },

    # --------------------------------------------------------------
    # DEMAND
    # --------------------------------------------------------------
    "Demand Forecast": {
        "model_candidates": [
            "demand_model.joblib",
            "demand_forecast_model.joblib",
        ],
        "data_candidates": [
            "demand_features.csv",
            "demand_dataset.csv",
        ],
    },

    # --------------------------------------------------------------
    # BUYER
    # --------------------------------------------------------------
    "Buyer Reliability": {
        "model_candidates": [
            "buyer_model.joblib",
        ],
        "data_candidates": [
            "buyer_features.csv",
        ],
    },

    # --------------------------------------------------------------
    # QUALITY
    # --------------------------------------------------------------
    "Quality Score": {
        "model_candidates": [
            "quality_score_model.joblib",
        ],
        "data_candidates": [
            "quality_features.csv",
        ],
    },

    "Quality Grade": {
        "model_candidates": [
            "quality_grade_model.joblib",
        ],
        "data_candidates": [
            "quality_features.csv",
        ],
    },

    "Spoilage Risk Score": {
        "model_candidates": [
            "spoilage_risk_score_model.joblib",
        ],
        "data_candidates": [
            "quality_features.csv",
        ],
    },

    "Spoilage Risk": {
        "model_candidates": [
            "spoilage_risk_model.joblib",
        ],
        "data_candidates": [
            "quality_features.csv",
        ],
    },

    # --------------------------------------------------------------
    # LOGISTICS
    # --------------------------------------------------------------
    "Transport Cost": {
        "model_candidates": [
            "transport_cost_model.joblib",
        ],
        "data_candidates": [
            "logistics_features.csv",
        ],
    },

    "Delay Hours": {
        "model_candidates": [
            "delay_hours_model.joblib",
        ],
        "data_candidates": [
            "logistics_features.csv",
        ],
    },

    "Damage Percentage": {
        "model_candidates": [
            "damage_percentage_model.joblib",
        ],
        "data_candidates": [
            "logistics_features.csv",
        ],
    },

    # --------------------------------------------------------------
    # COST
    # --------------------------------------------------------------
    "Cost Estimation": {
        "model_candidates": [
            "cost_estimation_model.joblib",
        ],
        "data_candidates": [
            "cost_features.csv",
        ],
    },

    # --------------------------------------------------------------
    # RISK
    # --------------------------------------------------------------
    "Payment Risk": {
        "model_candidates": [
            "payment_risk_model.joblib",
        ],
        "data_candidates": [
            "transaction_features.csv",
        ],
    },

    "Delivery Risk": {
        "model_candidates": [
            "delivery_risk_model.joblib",
        ],
        "data_candidates": [
            "transaction_features.csv",
        ],
    },
}


# ======================================================================
# HELPER FUNCTIONS
# ======================================================================

def find_existing_file(directory, candidates):
    """
    Find the first existing file from a list of candidates.
    """
    for filename in candidates:
        path = directory / filename

        if path.exists():
            return path

    return None


def get_model_feature_names(model):
    """
    Try to retrieve the exact feature names used during model training.

    Works especially well for sklearn Pipeline / ColumnTransformer models.
    """

    # Directly fitted model
    if hasattr(model, "feature_names_in_"):
        return list(model.feature_names_in_)

    # Pipeline
    if hasattr(model, "steps"):
        for _, step in reversed(model.steps):

            if hasattr(step, "feature_names_in_"):
                return list(step.feature_names_in_)

    return None


def prepare_features(model, df):
    """
    Select exactly the columns expected by the trained model.

    This prevents accidental changes to the feature order.
    """

    feature_names = get_model_feature_names(model)

    if feature_names is None:
        raise ValueError(
            "Could not determine the feature names expected by this model."
        )

    missing = [
        column
        for column in feature_names
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Dataset is missing model features: "
            + ", ".join(missing)
        )

    X = df[feature_names].copy()

    return X, feature_names


def validate_predictions(predictions, expected_rows):
    """
    Validate generated predictions.
    """

    predictions = np.asarray(predictions)

    # Flatten one-dimensional output
    if predictions.ndim == 1:
        prediction_count = len(predictions)

    else:
        prediction_count = predictions.shape[0]

    # --------------------------------------------------------------
    # Length check
    # --------------------------------------------------------------

    if prediction_count != expected_rows:
        return False, (
            f"Prediction length mismatch. "
            f"Expected {expected_rows}, got {prediction_count}"
        )

    # --------------------------------------------------------------
    # NaN check
    # --------------------------------------------------------------

    try:
        if np.isnan(predictions.astype(float)).any():
            return False, "Predictions contain NaN values."
    except (TypeError, ValueError):
        pass

    # --------------------------------------------------------------
    # Inf check
    # --------------------------------------------------------------

    try:
        if np.isinf(predictions.astype(float)).any():
            return False, "Predictions contain Inf values."
    except (TypeError, ValueError):
        pass

    # --------------------------------------------------------------
    # Constant prediction check
    # --------------------------------------------------------------

    if predictions.ndim == 1:

        if len(np.unique(predictions)) <= 1:
            return False, "Model produced only one unique prediction."

    return True, "Prediction validation passed."


def get_prediction_summary(predictions):
    """
    Generate a short prediction summary.
    """

    predictions = np.asarray(predictions)

    if predictions.ndim == 1:

        if np.issubdtype(predictions.dtype, np.number):

            return (
                f"min={np.min(predictions):.4f}, "
                f"max={np.max(predictions):.4f}, "
                f"mean={np.mean(predictions):.4f}"
            )

        unique_values = np.unique(predictions)

        return (
            f"unique_classes={len(unique_values)}, "
            f"classes={unique_values[:10]}"
        )

    return (
        f"shape={predictions.shape}"
    )


# ======================================================================
# TEST ONE MODEL
# ======================================================================

def test_model(model_name, config):

    print("\n" + "=" * 70)
    print(f"TESTING: {model_name}")
    print("=" * 70)

    # --------------------------------------------------------------
    # Find model
    # --------------------------------------------------------------

    model_path = find_existing_file(
        MODEL_DIR,
        config["model_candidates"]
    )

    if model_path is None:

        print("✗ MODEL NOT FOUND")

        print("\nChecked:")
        for filename in config["model_candidates"]:
            print(f"  - {MODEL_DIR / filename}")

        return False

    print("\nModel:")
    print(model_path)

    # --------------------------------------------------------------
    # Load model
    # --------------------------------------------------------------

    try:

        model = joblib.load(model_path)

        print("✓ Model loaded successfully.")

    except Exception as error:

        print("✗ MODEL LOAD FAILED")
        print(f"Error: {error}")

        return False

    # --------------------------------------------------------------
    # Find dataset
    # --------------------------------------------------------------

    data_path = find_existing_file(
        DATA_DIR,
        config["data_candidates"]
    )

    if data_path is None:

        print("\n✗ DATASET NOT FOUND")

        print("\nChecked:")
        for filename in config["data_candidates"]:
            print(f"  - {DATA_DIR / filename}")

        return False

    print("\nDataset:")
    print(data_path)

    # --------------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------------

    try:

        df = pd.read_csv(data_path)

        print("✓ Dataset loaded successfully.")
        print(f"Rows    : {len(df):,}")
        print(f"Columns : {len(df.columns):,}")

    except Exception as error:

        print("✗ DATASET LOAD FAILED")
        print(f"Error: {error}")

        return False

    # --------------------------------------------------------------
    # Prepare features
    # --------------------------------------------------------------

    try:

        X, feature_names = prepare_features(
            model,
            df
        )

        print("\nFeatures selected:")
        print(f"Feature count: {len(feature_names)}")

        print("✓ Model feature structure matched.")

    except Exception as error:

        print("\n✗ FEATURE PREPARATION FAILED")
        print(f"Error: {error}")

        return False

    # --------------------------------------------------------------
    # Generate predictions
    # --------------------------------------------------------------

    try:

        print("\nGenerating predictions...")

        predictions = model.predict(X)

        print("✓ Predictions generated successfully.")

    except Exception as error:

        print("\n✗ PREDICTION FAILED")
        print(f"Error: {error}")

        return False

    # --------------------------------------------------------------
    # Validate predictions
    # --------------------------------------------------------------

    valid, message = validate_predictions(
        predictions,
        len(X)
    )

    if not valid:

        print("\n✗ PREDICTION VALIDATION FAILED")
        print(message)

        return False

    print("✓ Prediction length is correct.")
    print("✓ No NaN / Inf predictions detected.")
    print("✓ Prediction output is valid.")

    # --------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------

    print("\nPrediction summary:")
    print(get_prediction_summary(predictions))

    print("\n✓", model_name.upper(), "PASSED")

    return True


# ======================================================================
# RUN ALL TESTS
# ======================================================================

results = {}

print("\n")
print("=" * 70)
print("STARTING COMPLETE MODEL TEST")
print("=" * 70)

for model_name, config in MODEL_CONFIG.items():

    try:

        results[model_name] = test_model(
            model_name,
            config
        )

    except Exception as error:

        print("\n✗ UNEXPECTED ERROR")
        print(f"{model_name}: {error}")

        results[model_name] = False


# ======================================================================
# FINAL SUMMARY
# ======================================================================

print("\n")
print("=" * 70)
print("FINAL MODEL TEST SUMMARY")
print("=" * 70)

passed = 0
failed = 0

for model_name, status in results.items():

    if status:

        print(f"✓ {model_name:<30} PASSED")
        passed += 1

    else:

        print(f"✗ {model_name:<30} FAILED")
        failed += 1


total = len(results)

print("\n" + "-" * 70)

print(f"Total models tested : {total}")
print(f"Models passed       : {passed}")
print(f"Models failed       : {failed}")

print("-" * 70)


# ======================================================================
# FINAL RESULT
# ======================================================================

if failed == 0:

    print("\n" + "=" * 70)
    print("✓ ALL MODELS PASSED")
    print("=" * 70)

    print("\nAll saved models:")
    print("✓ Loaded successfully")
    print("✓ Accepted their feature datasets")
    print("✓ Generated predictions")
    print("✓ Produced correct prediction lengths")
    print("✓ Produced no NaN / Inf predictions")

    print("\nAI MODEL LAYER IS READY.")

else:

    print("\n" + "=" * 70)
    print("⚠ SOME MODELS FAILED")
    print("=" * 70)

    print("\nFix the failed models before moving to")
    print("the Decision Intelligence Engine.")

print("\n")