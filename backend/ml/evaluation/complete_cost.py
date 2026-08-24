"""
======================================================================
COST ESTIMATION MODEL COMPLETION VERIFICATION
======================================================================

Existing architecture only.
Existing trained model only.
Existing processed dataset only.

No model retraining.
No dataset modification.
No fake predictions.
No new architecture components.
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
# PROJECT PATHS
# ======================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


DATA_DIR = PROJECT_ROOT / "data" / "processed"

MODEL_DIR = (
    PROJECT_ROOT
    / "backend"
    / "ml"
    / "saved_models"
)


# ======================================================================
# EXISTING DATASET AND MODEL
# ======================================================================

COST_DATA_PATH = (
    DATA_DIR / "cost_features.csv"
)

COST_MODEL_PATH = (
    MODEL_DIR / "cost_estimation_model.joblib"
)


# ======================================================================
# DISPLAY HELPERS
# ======================================================================

def separator():
    print("=" * 70)


def section(title):

    print()
    separator()
    print(title)
    separator()


# ======================================================================
# TARGET DISCOVERY
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
# MODEL FEATURE DISCOVERY
# ======================================================================

def get_model_features(model):

    if hasattr(
        model,
        "feature_names_in_"
    ):

        return list(
            model.feature_names_in_
        )

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

    return None


# ======================================================================
# FEATURE PREPARATION
# ======================================================================

def prepare_model_input(
    model,
    dataframe
):

    model_features = get_model_features(
        model
    )

    if model_features:

        missing = [
            column
            for column in model_features
            if column not in dataframe.columns
        ]

        if missing:

            return None, missing

        return (
            dataframe[
                model_features
            ].copy(),
            []
        )

    # Fallback:
    # Pass the existing dataset to the saved Pipeline.
    # The Pipeline is responsible for preprocessing.

    return dataframe.copy(), []


# ======================================================================
# COST MODEL VERIFICATION
# ======================================================================

def verify_cost_model(
    model,
    dataframe
):

    section(
        "COST ESTIMATION MODEL VERIFICATION"
    )

    result = {
        "complete": False,
        "metrics": None,
    }

    print(
        "[1] Checking Cost Estimation model..."
    )

    print(
        "✓ Cost Estimation model loaded"
    )

    # ------------------------------------------------------------------
    # TARGET
    # ------------------------------------------------------------------

    target_column = find_target_column(
        dataframe,
        [
            "total_cost",
            "estimated_total_cost",
            "cost_estimation",
            "estimated_cost",
            "total_cost_inr",
            "cost",
        ]
    )

    if target_column is None:

        print(
            "✗ Cost target column not found"
        )

        print(
            "Available columns:"
        )

        for column in dataframe.columns:

            print(
                f"  - {column}"
            )

        return result

    print(
        f"✓ Target: {target_column}"
    )

    # ------------------------------------------------------------------
    # TARGET VALIDATION
    # ------------------------------------------------------------------

    target = pd.to_numeric(
        dataframe[target_column],
        errors="coerce"
    )

    valid_mask = (
        target.notna()
        &
        np.isfinite(
            target.to_numpy(
                dtype=float
            )
        )
    )

    evaluation_data = (
        dataframe.loc[
            valid_mask
        ].copy()
    )

    y_true = (
        target.loc[
            valid_mask
        ]
        .astype(float)
        .to_numpy()
    )

    invalid_target_count = (
        len(dataframe)
        -
        len(y_true)
    )

    print(
        f"Valid target rows: "
        f"{len(y_true):,}"
    )

    print(
        f"Invalid target rows: "
        f"{invalid_target_count:,}"
    )

    if len(y_true) == 0:

        print(
            "✗ No valid target rows"
        )

        return result

    # ------------------------------------------------------------------
    # FEATURES
    # ------------------------------------------------------------------

    X, missing = prepare_model_input(
        model,
        evaluation_data
    )

    if X is None:

        print(
            "✗ Missing required model features:"
        )

        for column in missing:

            print(
                f"  - {column}"
            )

        return result

    print(
        f"✓ Features prepared: "
        f"{X.shape[1]}"
    )

    print(
        f"X shape: {X.shape}"
    )

    # ------------------------------------------------------------------
    # PREDICTIONS
    # ------------------------------------------------------------------

    print(
        "\n[2] Running Cost Estimation predictions..."
    )

    try:

        predictions = model.predict(
            X
        )

    except Exception as exc:

        print(
            "✗ Prediction failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return result

    try:

        predictions = np.asarray(
            predictions,
            dtype=float
        )

    except Exception as exc:

        print(
            "✗ Predictions are not numeric"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return result

    # ------------------------------------------------------------------
    # PREDICTION VALIDATION
    # ------------------------------------------------------------------

    invalid_predictions = int(
        np.count_nonzero(
            ~np.isfinite(
                predictions
            )
        )
    )

    print(
        f"Prediction count: "
        f"{len(predictions):,}"
    )

    print(
        f"Invalid predictions: "
        f"{invalid_predictions:,}"
    )

    if invalid_predictions > 0:

        print(
            "✗ Invalid predictions detected"
        )

        return result

    if len(predictions) != len(y_true):

        print(
            "✗ Prediction/target count mismatch"
        )

        return result

    print(
        "✓ Cost predictions valid"
    )

    print(
        f"Prediction range: "
        f"{predictions.min():.4f} "
        f"to "
        f"{predictions.max():.4f}"
    )

    # ------------------------------------------------------------------
    # METRICS
    # ------------------------------------------------------------------

    print(
        "\n[3] Calculating Cost Estimation metrics..."
    )

    try:

        mae = mean_absolute_error(
            y_true,
            predictions
        )

        rmse = float(
            np.sqrt(
                mean_squared_error(
                    y_true,
                    predictions
                )
            )
        )

        r2 = r2_score(
            y_true,
            predictions
        )

    except Exception as exc:

        print(
            "✗ Metric calculation failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return result

    print()
    print(
        "COST ESTIMATION METRICS"
    )

    print(
        "-" * 70
    )

    print(
        f"MAE  : {mae:.6f}"
    )

    print(
        f"RMSE : {rmse:.6f}"
    )

    print(
        f"R²   : {r2:.6f}"
    )

    result["metrics"] = {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
    }

    result["complete"] = True

    print(
        "\n✓ COST ESTIMATION MODEL VERIFIED"
    )

    return result


# ======================================================================
# PREDICTION SERVICE INTEGRATION
# ======================================================================

def check_prediction_service():

    print()
    print(
        "[PredictionService] Checking integration..."
    )

    try:

        from backend.app.decision.prediction_service import (
            PredictionService
        )

        service = PredictionService()

        if not hasattr(
            service,
            "models"
        ):

            print(
                "✗ PredictionService has no "
                "'models' registry"
            )

            return False

        if "cost" not in service.models:

            print(
                "✗ PredictionService does not "
                "contain 'cost' model"
            )

            return False

        print(
            "✓ PredictionService contains "
            "'cost' model"
        )

        return True

    except Exception as exc:

        print(
            "✗ PredictionService check failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return False


# ======================================================================
# MAIN
# ======================================================================

def main():

    section(
        "COST ESTIMATION FINAL COMPLETION CHECK"
    )

    print(
        "Using existing architecture only."
    )

    print(
        "Using existing trained model only."
    )

    print(
        "Using existing processed dataset only."
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
    # DATASET
    # ==================================================================

    print(
        "\n[1] Checking Cost dataset..."
    )

    if not COST_DATA_PATH.exists():

        print(
            "✗ Cost dataset not found:"
        )

        print(
            COST_DATA_PATH
        )

        print(
            "\nAvailable CSV files:"
        )

        for path in sorted(
            DATA_DIR.glob("*.csv")
        ):

            print(
                f"  - {path.name}"
            )

        return

    print(
        "✓ Cost dataset exists"
    )

    print(
        COST_DATA_PATH
    )

    # ==================================================================
    # MODEL
    # ==================================================================

    print(
        "\n[2] Checking Cost model..."
    )

    if not COST_MODEL_PATH.exists():

        print(
            "✗ Cost Estimation model not found:"
        )

        print(
            COST_MODEL_PATH
        )

        return

    print(
        "✓ Cost Estimation model exists"
    )

    # ==================================================================
    # LOAD DATASET
    # ==================================================================

    print(
        "\n[3] Loading Cost dataset..."
    )

    try:

        dataframe = pd.read_csv(
            COST_DATA_PATH
        )

    except Exception as exc:

        print(
            "✗ Dataset loading failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return

    print(
        "✓ Cost dataset loaded"
    )

    print(
        f"  Rows    : "
        f"{len(dataframe):,}"
    )

    print(
        f"  Columns : "
        f"{len(dataframe.columns)}"
    )

    # ==================================================================
    # LOAD MODEL
    # ==================================================================

    print(
        "\n[4] Loading trained Cost model..."
    )

    try:

        cost_model = joblib.load(
            COST_MODEL_PATH
        )

    except Exception as exc:

        print(
            "✗ Cost model loading failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return

    print(
        "✓ Cost Estimation model loaded"
    )

    print(
        f"  Type: "
        f"{type(cost_model).__name__}"
    )

    # ==================================================================
    # VERIFY MODEL
    # ==================================================================

    result = verify_cost_model(
        cost_model,
        dataframe
    )

    # ==================================================================
    # PREDICTION SERVICE
    # ==================================================================

    service_valid = (
        check_prediction_service()
    )

    # ==================================================================
    # FINAL STATUS
    # ==================================================================

    section(
        "COST ESTIMATION FINAL STATUS"
    )

    print(
        "Cost Estimation : "
        +
        (
            "✓ COMPLETED"
            if result["complete"]
            else "⚠ INCOMPLETE"
        )
    )

    print(
        "PredictionService: "
        +
        (
            "✓ VERIFIED"
            if service_valid
            else "⚠ FAILED"
        )
    )

    final_complete = (
        result["complete"]
        and service_valid
    )

    print()

    separator()

    if final_complete:

        print(
            "✓ COST ESTIMATION FULLY COMPLETED"
        )

        print(
            "✓ Existing Cost model verified"
        )

        print(
            "✓ Existing Cost dataset verified"
        )

        print(
            "✓ Real predictions verified"
        )

        print(
            "✓ Evaluation metrics verified"
        )

        print(
            "✓ PredictionService integration verified"
        )

        print()
        print(
            "Next existing architecture component: "
            "RISK"
        )

    else:

        print(
            "⚠ COST ESTIMATION NOT YET COMPLETED"
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

    except KeyboardInterrupt:

        print()
        print(
            "⚠ Verification interrupted by user."
        )

        sys.exit(1)

    except Exception as exc:

        print()
        separator()

        print(
            "FATAL VERIFICATION ERROR"
        )

        separator()

        print(
            f"{type(exc).__name__}: {exc}"
        )

        print()
        print(
            "Traceback:"
        )

        traceback.print_exc()

        sys.exit(1)