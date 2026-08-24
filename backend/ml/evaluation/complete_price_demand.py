"""
======================================================================
PRICE + DEMAND MODEL COMPLETION VERIFICATION
======================================================================

Existing architecture only.
Existing trained models only.
Existing processed datasets only.

This script:
- loads existing Price and Demand models
- validates existing datasets
- preserves categorical features
- runs real predictions through the saved Pipelines
- calculates MAE, RMSE and R²
- verifies PredictionService integration
- reports final completion status

NO:
- model retraining
- new models
- new datasets
- fake predictions
- dataset modification
- architecture changes
======================================================================
"""

from pathlib import Path
import sys
import traceback

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


# ======================================================================
# PROJECT PATH
# ======================================================================

# File:
# backend/ml/evaluation/complete_price_demand.py
#
# parents[0] = evaluation
# parents[1] = ml
# parents[2] = backend
# parents[3] = PythonProject3

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ======================================================================
# DIRECTORIES
# ======================================================================

DATA_DIR = PROJECT_ROOT / "data" / "processed"

MODEL_DIR = (
    PROJECT_ROOT
    / "backend"
    / "ml"
    / "saved_models"
)


# ======================================================================
# MODEL PATHS
# ======================================================================

PRICE_MODEL_PATH = (
    MODEL_DIR / "price_model.joblib"
)

DEMAND_MODEL_PATH = (
    MODEL_DIR / "demand_model.joblib"
)


# ======================================================================
# DATA PATHS
# ======================================================================

PRICE_DATA_PATH = (
    DATA_DIR / "price_features.csv"
)

DEMAND_DATA_PATH = (
    DATA_DIR / "demand_features.csv"
)


# ======================================================================
# DISPLAY HELPERS
# ======================================================================

def separator():
    print("=" * 70)


def section(title):

    print("\n")
    separator()
    print(title)
    separator()


# ======================================================================
# TARGET SEARCH
# ======================================================================

def find_target_column(
    dataframe,
    candidates
):

    for column in candidates:

        if column in dataframe.columns:
            return column

    return None


# ======================================================================
# MODEL FEATURE SEARCH
# ======================================================================

def get_model_features(
    model,
    dataframe,
    target_column
):

    # --------------------------------------------------------------
    # Direct feature_names_in_
    # --------------------------------------------------------------

    if hasattr(
        model,
        "feature_names_in_"
    ):

        return list(
            model.feature_names_in_
        )

    # --------------------------------------------------------------
    # Pipeline
    # --------------------------------------------------------------

    if hasattr(
        model,
        "named_steps"
    ):

        for _, step in model.named_steps.items():

            if hasattr(
                step,
                "feature_names_in_"
            ):

                return list(
                    step.feature_names_in_
                )

    # --------------------------------------------------------------
    # Fallback
    # --------------------------------------------------------------

    return [

        column

        for column in dataframe.columns

        if column != target_column
    ]


# ======================================================================
# PREDICTION SERVICE CHECK
# ======================================================================

def check_prediction_service(
    model_name
):

    print(
        "\n[11] Checking PredictionService..."
    )

    try:

        # Actual project location:
        # backend/app/decision/prediction_service.py

        from backend.app.decision.prediction_service import (
            PredictionService
        )

        service = PredictionService()

        model_key = (
            "price"
            if model_name.lower() == "price"
            else "demand"
        )

        # ----------------------------------------------------------
        # Check model registry
        # ----------------------------------------------------------

        if not hasattr(
            service,
            "models"
        ):

            print(
                "✗ PredictionService does not "
                "expose a models registry."
            )

            return False

        if model_key not in service.models:

            print(
                f"✗ '{model_key}' model is not "
                f"registered in PredictionService."
            )

            return False

        print(
            f"✓ PredictionService contains "
            f"'{model_key}' model"
        )

        return True

    except ModuleNotFoundError as exc:

        print(
            "✗ PredictionService import failed:"
        )

        print(
            f"  {exc}"
        )

        return False

    except Exception as exc:

        print(
            "✗ PredictionService check failed:"
        )

        print(
            f"  {type(exc).__name__}: {exc}"
        )

        return False


# ======================================================================
# MODEL VERIFICATION
# ======================================================================

def verify_model(
    name,
    model_path,
    data_path,
    target_candidates
):

    result = {

        "model_exists": False,

        "dataset_exists": False,

        "model_loaded": False,

        "target_found": False,

        "features_valid": False,

        "prediction_success": False,

        "predictions_valid": False,

        "shape_valid": False,

        "metrics_valid": False,

        "service_valid": False,

        "metrics": None,

        "error": None,
    }

    section(
        f"{name.upper()} MODEL COMPLETION VERIFICATION"
    )

    # ==================================================================
    # 1. MODEL
    # ==================================================================

    print(
        "\n[1] Checking saved model..."
    )

    if not model_path.exists():

        print(
            "✗ Model not found:"
        )

        print(
            model_path
        )

        result["error"] = (
            "Model file not found"
        )

        return result

    result["model_exists"] = True

    print(
        "✓ Model exists"
    )

    print(
        model_path
    )

    # ==================================================================
    # 2. DATASET
    # ==================================================================

    print(
        "\n[2] Checking existing processed dataset..."
    )

    if not data_path.exists():

        print(
            "✗ Dataset not found:"
        )

        print(
            data_path
        )

        result["error"] = (
            "Dataset file not found"
        )

        return result

    result["dataset_exists"] = True

    print(
        "✓ Existing dataset found"
    )

    print(
        f"  {data_path.name}"
    )

    # ==================================================================
    # 3. LOAD MODEL
    # ==================================================================

    print(
        "\n[3] Loading trained model..."
    )

    try:

        model = joblib.load(
            model_path
        )

        result["model_loaded"] = True

        print(
            "✓ Model loaded"
        )

        print(
            f"  Type: {type(model).__name__}"
        )

    except Exception as exc:

        print(
            "✗ Model loading failed"
        )

        print(
            f"  {type(exc).__name__}: {exc}"
        )

        result["error"] = str(exc)

        return result

    # ==================================================================
    # 4. LOAD DATA
    # ==================================================================

    print(
        "\n[4] Loading evaluation dataset..."
    )

    try:

        dataframe = pd.read_csv(
            data_path
        )

        print(
            "✓ Dataset loaded"
        )

        print(
            f"  Rows    : {len(dataframe):,}"
        )

        print(
            f"  Columns : {len(dataframe.columns)}"
        )

    except Exception as exc:

        print(
            "✗ Dataset loading failed"
        )

        print(
            f"  {type(exc).__name__}: {exc}"
        )

        result["error"] = str(exc)

        return result

    # ==================================================================
    # 5. TARGET
    # ==================================================================

    print(
        "\n[5] Finding target column..."
    )

    target_column = find_target_column(
        dataframe,
        target_candidates
    )

    if target_column is None:

        print(
            "✗ Target column not found"
        )

        print(
            "\nAvailable columns:"
        )

        for column in dataframe.columns:

            print(
                f"  - {column}"
            )

        result["error"] = (
            "Target column not found"
        )

        return result

    result["target_found"] = True

    print(
        f"✓ Target: {target_column}"
    )

    # ==================================================================
    # 6. TARGET VALIDATION
    # ==================================================================

    print(
        "\n[6] Validating target..."
    )

    target = pd.to_numeric(
        dataframe[target_column],
        errors="coerce"
    )

    valid_mask = (
        target.notna()
        &
        np.isfinite(target)
    )

    dataframe_valid = dataframe.loc[
        valid_mask
    ].copy()

    y = target.loc[
        valid_mask
    ].astype(float).to_numpy()

    print(
        f"Valid rows   : {len(y):,}"
    )

    print(
        f"Invalid rows : "
        f"{len(dataframe) - len(y):,}"
    )

    if len(y) == 0:

        print(
            "✗ No valid target rows"
        )

        result["error"] = (
            "No valid target rows"
        )

        return result

    # ==================================================================
    # 7. FEATURES
    # ==================================================================

    print(
        "\n[7] Preparing model features..."
    )

    try:

        feature_names = get_model_features(
            model,
            dataframe_valid,
            target_column
        )

        missing_features = [

            feature

            for feature in feature_names

            if feature not in dataframe_valid.columns
        ]

        if missing_features:

            print(
                "✗ Missing model features:"
            )

            for feature in missing_features:

                print(
                    f"  - {feature}"
                )

            result["error"] = (
                "Missing model features"
            )

            return result

        # IMPORTANT:
        # Keep categorical values exactly as they are.
        #
        # The saved Pipeline contains the preprocessing
        # required by the model.

        X = dataframe_valid[
            feature_names
        ].copy()

        result["features_valid"] = True

        print(
            f"✓ Features prepared: "
            f"{len(feature_names)}"
        )

        print(
            f"X shape: {X.shape}"
        )

        categorical_columns = [

            column

            for column in X.columns

            if not pd.api.types.is_numeric_dtype(
                X[column]
            )
        ]

        if categorical_columns:

            print(
                "Categorical features preserved:"
            )

            for column in categorical_columns:

                print(
                    f"  - {column}"
                )

    except Exception as exc:

        print(
            "✗ Feature preparation failed"
        )

        print(
            f"  {type(exc).__name__}: {exc}"
        )

        result["error"] = str(exc)

        return result

    # ==================================================================
    # 8. PREDICTION
    # ==================================================================

    print(
        "\n[8] Running Pipeline prediction..."
    )

    try:

        predictions = model.predict(
            X
        )

        result["prediction_success"] = True

        print(
            "✓ Pipeline prediction completed"
        )

    except Exception as exc:

        print(
            "✗ Pipeline prediction failed"
        )

        print(
            f"  {type(exc).__name__}: {exc}"
        )

        result["error"] = str(exc)

        return result

    # ==================================================================
    # 9. PREDICTION VALIDATION
    # ==================================================================

    print(
        "\n[9] Validating predictions..."
    )

    predictions = np.asarray(
        predictions,
        dtype=float
    )

    print(
        f"Prediction shape: "
        f"{predictions.shape}"
    )

    invalid_count = int(
        (~np.isfinite(predictions)).sum()
    )

    print(
        f"Invalid predictions: "
        f"{invalid_count}"
    )

    if invalid_count > 0:

        print(
            "✗ NaN or infinite predictions found"
        )

        result["error"] = (
            "Invalid predictions"
        )

        return result

    result["predictions_valid"] = True

    if len(predictions) != len(y):

        print(
            "✗ Prediction count mismatch"
        )

        print(
            f"Predictions: {len(predictions)}"
        )

        print(
            f"Targets    : {len(y)}"
        )

        result["error"] = (
            "Prediction/target count mismatch"
        )

        return result

    result["shape_valid"] = True

    print(
        "✓ Prediction count matches target count"
    )

    print(
        f"Prediction range: "
        f"{predictions.min():.4f} "
        f"to "
        f"{predictions.max():.4f}"
    )

    # ==================================================================
    # 10. METRICS
    # ==================================================================

    print(
        "\n[10] Calculating test metrics..."
    )

    try:

        mae = mean_absolute_error(
            y,
            predictions
        )

        rmse = np.sqrt(
            mean_squared_error(
                y,
                predictions
            )
        )

        r2 = r2_score(
            y,
            predictions
        )

        result["metrics"] = {

            "mae": float(mae),

            "rmse": float(rmse),

            "r2": float(r2),
        }

        result["metrics_valid"] = True

        print(
            f"MAE  : {mae:.6f}"
        )

        print(
            f"RMSE : {rmse:.6f}"
        )

        print(
            f"R²   : {r2:.6f}"
        )

    except Exception as exc:

        print(
            "✗ Metric calculation failed"
        )

        print(
            f"  {type(exc).__name__}: {exc}"
        )

        result["error"] = str(exc)

        return result

    # ==================================================================
    # 11. PREDICTION SERVICE
    # ==================================================================

    result["service_valid"] = check_prediction_service(
        name
    )

    # ==================================================================
    # COMPONENT STATUS
    # ==================================================================

    completed = all([

        result["model_exists"],

        result["dataset_exists"],

        result["model_loaded"],

        result["target_found"],

        result["features_valid"],

        result["prediction_success"],

        result["predictions_valid"],

        result["shape_valid"],

        result["metrics_valid"],

        result["service_valid"],
    ])

    print(
        "\n"
    )

    if completed:

        print(
            f"✓ {name.upper()} FULLY COMPLETED"
        )

    else:

        print(
            f"⚠ {name.upper()} NOT FULLY COMPLETED"
        )

    return result


# ======================================================================
# MAIN
# ======================================================================

def main():

    section(
        "PRICE + DEMAND FINAL COMPLETION CHECK"
    )

    print(
        "Using existing architecture only."
    )

    print(
        "Using existing trained models only."
    )

    print(
        "Using existing processed datasets only."
    )

    print(
        "No model retraining."
    )

    print(
        "No dataset modification."
    )

    print(
        "No fake predictions."
    )

    # ==================================================================
    # PRICE
    # ==================================================================

    price_result = verify_model(

        name="Price",

        model_path=PRICE_MODEL_PATH,

        data_path=PRICE_DATA_PATH,

        target_candidates=[

            "modal_price_per_quintal",

            "target",

            "price",

            "price_per_quintal",
        ],
    )

    # ==================================================================
    # DEMAND
    # ==================================================================

    demand_result = verify_model(

        name="Demand",

        model_path=DEMAND_MODEL_PATH,

        data_path=DEMAND_DATA_PATH,

        target_candidates=[

            "estimated_demand_tonnes",

            "current_demand_tonnes",

            "demand",

            "target",

            "demand_tonnes",
        ],
    )

    # ==================================================================
    # FINAL STATUS
    # ==================================================================

    section(
        "FINAL COMPONENT STATUS"
    )

    def is_complete(result):

        return all([

            result["model_exists"],

            result["dataset_exists"],

            result["model_loaded"],

            result["target_found"],

            result["features_valid"],

            result["prediction_success"],

            result["predictions_valid"],

            result["shape_valid"],

            result["metrics_valid"],

            result["service_valid"],
        ])

    price_complete = is_complete(
        price_result
    )

    demand_complete = is_complete(
        demand_result
    )

    print(
        f"Price : "
        f"{'✓ COMPLETED' if price_complete else '⚠ INCOMPLETE'}"
    )

    print(
        f"Demand: "
        f"{'✓ COMPLETED' if demand_complete else '⚠ INCOMPLETE'}"
    )

    # ==================================================================
    # METRIC SUMMARY
    # ==================================================================

    if price_result["metrics"]:

        print(
            "\nPRICE METRICS"
        )

        print(
            "-" * 70
        )

        print(
            f"MAE  : "
            f"{price_result['metrics']['mae']:.6f}"
        )

        print(
            f"RMSE : "
            f"{price_result['metrics']['rmse']:.6f}"
        )

        print(
            f"R²   : "
            f"{price_result['metrics']['r2']:.6f}"
        )

    if demand_result["metrics"]:

        print(
            "\nDEMAND METRICS"
        )

        print(
            "-" * 70
        )

        print(
            f"MAE  : "
            f"{demand_result['metrics']['mae']:.6f}"
        )

        print(
            f"RMSE : "
            f"{demand_result['metrics']['rmse']:.6f}"
        )

        print(
            f"R²   : "
            f"{demand_result['metrics']['r2']:.6f}"
        )

    # ==================================================================
    # FINAL MESSAGE
    # ==================================================================

    print(
        "\n"
    )

    separator()

    if price_complete and demand_complete:

        print(
            "✓ PRICE + DEMAND ARE FULLY COMPLETED"
        )

        print(
            "✓ Existing models verified"
        )

        print(
            "✓ Existing datasets verified"
        )

        print(
            "✓ Pipeline predictions verified"
        )

        print(
            "✓ Evaluation metrics verified"
        )

        print(
            "✓ PredictionService integration verified"
        )

        print(
            "\nNext existing architecture component "
            "can be completed."
        )

    else:

        print(
            "⚠ PRICE + DEMAND ARE NOT YET "
            "FULLY COMPLETED"
        )

        print(
            "Review the failed checks above."
        )

    separator()


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":

    try:

        main()

    except Exception as exc:

        print("\n")
        separator()

        print(
            "FATAL VERIFICATION ERROR"
        )

        separator()

        print(
            f"{type(exc).__name__}: {exc}"
        )

        print(
            "\nTraceback:"
        )

        traceback.print_exc()

        sys.exit(1)