"""
LOGISTICS MODEL COMPLETION VERIFICATION

Existing architecture only.
Existing trained models only.
Existing processed dataset only.

Logistics components:
    1. Transport Cost
    2. Delay Hours
    3. Damage Percentage

No:
    - model retraining
    - new datasets
    - dataset modification
    - fake predictions
    - architecture changes
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
# EXISTING DATASET
# ======================================================================

LOGISTICS_DATA_PATH = (
    DATA_DIR / "logistics_features.csv"
)


# ======================================================================
# EXISTING MODELS
# ======================================================================

TRANSPORT_COST_MODEL_PATH = (
    MODEL_DIR / "transport_cost_model.joblib"
)

DELAY_MODEL_PATH = (
    MODEL_DIR / "delay_hours_model.joblib"
)

DAMAGE_MODEL_PATH = (
    MODEL_DIR / "damage_percentage_model.joblib"
)


# ======================================================================
# DISPLAY
# ======================================================================

def separator():
    print("=" * 70)


def section(title):

    print()
    separator()
    print(title)
    separator()


# ======================================================================
# TARGET FINDER
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

        if not missing:

            return (
                dataframe[
                    model_features
                ].copy(),
                []
            )

        return None, missing

    # ------------------------------------------------------------------
    # Fallback: use existing dataset columns.
    # The saved Pipeline handles its own preprocessing.
    # ------------------------------------------------------------------

    X = dataframe.copy()

    return X, []


# ======================================================================
# NUMERIC TARGET
# ======================================================================

def prepare_numeric_target(
    dataframe,
    target_column
):

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

    return evaluation_data, y_true


# ======================================================================
# SINGLE REGRESSION MODEL VERIFICATION
# ======================================================================

def verify_regression_model(
    model_name,
    model,
    dataframe,
    target_candidates
):

    section(
        f"{model_name.upper()} MODEL VERIFICATION"
    )

    result = {
        "complete": False,
        "metrics": None,
    }

    # ------------------------------------------------------------------
    # TARGET
    # ------------------------------------------------------------------

    target_column = find_target_column(
        dataframe,
        target_candidates
    )

    if target_column is None:

        print(
            "✗ Target column not found"
        )

        print(
            "Expected one of:"
        )

        for candidate in target_candidates:

            print(
                f"  - {candidate}"
            )

        return result

    print(
        f"✓ Target: {target_column}"
    )

    # ------------------------------------------------------------------
    # TARGET VALIDATION
    # ------------------------------------------------------------------

    evaluation_data, y_true = (
        prepare_numeric_target(
            dataframe,
            target_column
        )
    )

    print(
        f"Valid target rows: "
        f"{len(y_true):,}"
    )

    invalid_target_count = (
        len(dataframe)
        -
        len(y_true)
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
            "✗ Missing model features:"
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
        "\nRunning real model predictions..."
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
            "✗ Predictions could not "
            "be converted to numeric values"
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
        "✓ All predictions are valid"
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
        "\nCalculating evaluation metrics..."
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
        f"{model_name.upper()} METRICS"
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
        f"\n✓ {model_name.upper()} MODEL VERIFIED"
    )

    return result


# ======================================================================
# PREDICTION SERVICE
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

        required_models = [
            "transport_cost",
            "delay_hours",
            "damage_percentage",
        ]

        missing = [
            name
            for name in required_models
            if name not in service.models
        ]

        if missing:

            print(
                "✗ Missing Logistics models:"
            )

            for name in missing:

                print(
                    f"  - {name}"
                )

            return False

        for name in required_models:

            print(
                f"✓ PredictionService contains "
                f"'{name}'"
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
        "LOGISTICS MODEL COMPLETION CHECK"
    )

    print(
        "Using existing architecture only."
    )

    print(
        "Using existing trained models only."
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
        "\n[1] Checking Logistics dataset..."
    )

    if not LOGISTICS_DATA_PATH.exists():

        print(
            "✗ Logistics dataset not found:"
        )

        print(
            LOGISTICS_DATA_PATH
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
        "✓ Logistics dataset exists"
    )

    print(
        LOGISTICS_DATA_PATH
    )

    # ==================================================================
    # MODEL FILES
    # ==================================================================

    print(
        "\n[2] Checking Logistics models..."
    )

    model_paths = {

        "Transport Cost":
            TRANSPORT_COST_MODEL_PATH,

        "Delay Hours":
            DELAY_MODEL_PATH,

        "Damage Percentage":
            DAMAGE_MODEL_PATH,
    }

    for name, path in model_paths.items():

        if not path.exists():

            print(
                f"✗ {name} model not found:"
            )

            print(
                path
            )

            return

        print(
            f"✓ {name} model exists"
        )

    # ==================================================================
    # LOAD DATASET
    # ==================================================================

    print(
        "\n[3] Loading Logistics dataset..."
    )

    try:

        dataframe = pd.read_csv(
            LOGISTICS_DATA_PATH
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
        "✓ Logistics dataset loaded"
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
    # LOAD MODELS
    # ==================================================================

    print(
        "\n[4] Loading trained Logistics models..."
    )

    try:

        transport_model = joblib.load(
            TRANSPORT_COST_MODEL_PATH
        )

        delay_model = joblib.load(
            DELAY_MODEL_PATH
        )

        damage_model = joblib.load(
            DAMAGE_MODEL_PATH
        )

    except Exception as exc:

        print(
            "✗ Model loading failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return

    print(
        "✓ Transport Cost model loaded"
    )

    print(
        f"  Type: "
        f"{type(transport_model).__name__}"
    )

    print(
        "✓ Delay Hours model loaded"
    )

    print(
        f"  Type: "
        f"{type(delay_model).__name__}"
    )

    print(
        "✓ Damage Percentage model loaded"
    )

    print(
        f"  Type: "
        f"{type(damage_model).__name__}"
    )

    # ==================================================================
    # TRANSPORT COST
    # ==================================================================

    transport_result = verify_regression_model(

        "Transport Cost",

        transport_model,

        dataframe,

        [
            "transport_cost",
            "transport_cost_inr",
            "estimated_transport_cost",
            "transport_cost_rupees",
        ]
    )

    # ==================================================================
    # DELAY
    # ==================================================================

    delay_result = verify_regression_model(

        "Delay Hours",

        delay_model,

        dataframe,

        [
            "delay_hours",
            "estimated_delay_hours",
            "delay",
        ]
    )

    # ==================================================================
    # DAMAGE
    # ==================================================================

    damage_result = verify_regression_model(

        "Damage Percentage",

        damage_model,

        dataframe,

        [
            "damage_percentage",
            "damaged_percentage",
            "estimated_damage_percentage",
            "damage_percent",
        ]
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
        "LOGISTICS FINAL STATUS"
    )

    transport_complete = (
        transport_result["complete"]
    )

    delay_complete = (
        delay_result["complete"]
    )

    damage_complete = (
        damage_result["complete"]
    )

    print(
        "Transport Cost      : "
        +
        (
            "✓ COMPLETED"
            if transport_complete
            else "⚠ INCOMPLETE"
        )
    )

    print(
        "Delay Hours         : "
        +
        (
            "✓ COMPLETED"
            if delay_complete
            else "⚠ INCOMPLETE"
        )
    )

    print(
        "Damage Percentage   : "
        +
        (
            "✓ COMPLETED"
            if damage_complete
            else "⚠ INCOMPLETE"
        )
    )

    print(
        "PredictionService   : "
        +
        (
            "✓ VERIFIED"
            if service_valid
            else "⚠ FAILED"
        )
    )

    final_complete = (
        transport_complete
        and delay_complete
        and damage_complete
        and service_valid
    )

    print()

    separator()

    if final_complete:

        print(
            "✓ LOGISTICS FULLY COMPLETED"
        )

        print(
            "✓ Transport Cost model verified"
        )

        print(
            "✓ Delay Hours model verified"
        )

        print(
            "✓ Damage Percentage model verified"
        )

        print(
            "✓ Existing dataset verified"
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
            "COST ESTIMATION"
        )

    else:

        print(
            "⚠ LOGISTICS NOT YET COMPLETED"
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