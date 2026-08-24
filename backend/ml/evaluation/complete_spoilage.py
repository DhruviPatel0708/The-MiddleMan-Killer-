"""
======================================================================
SPOILAGE PREDICTION MODEL COMPLETION VERIFICATION
======================================================================

Existing architecture only.
Existing trained models only.
Existing processed dataset only.

Components:
    1. Spoilage Risk Score
    2. Spoilage Risk

No:
    - model retraining
    - new datasets
    - dataset modification
    - fake predictions
    - new architecture components
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
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
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
# EXISTING SPOILAGE DATASET
# ======================================================================

# Existing project dataset.
# We intentionally do NOT create spoilage.csv.
SPOILAGE_DATA_PATH = (
    DATA_DIR / "quality_features.csv"
)


# ======================================================================
# EXISTING SPOILAGE MODELS
# ======================================================================

SPOILAGE_SCORE_MODEL_PATH = (
    MODEL_DIR
    / "spoilage_risk_score_model.joblib"
)

SPOILAGE_RISK_MODEL_PATH = (
    MODEL_DIR
    / "spoilage_risk_model.joblib"
)


# ======================================================================
# DISPLAY HELPERS
# ======================================================================

def separator():

    print(
        "=" * 70
    )


def section(title):

    print()
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
# SPOILAGE FEATURE PREPARATION
# ======================================================================

def prepare_spoilage_features(
    dataframe
):

    # First try the exact features used by the existing
    # saved model.

    numeric_candidates = [
        "moisture_percentage",
        "foreign_matter_percentage",
        "damaged_percentage",
        "discolored_percentage",
        "insect_damage_percentage",
        "storage_days",
        "storage_temperature_c",
        "storage_humidity_percentage",
        "total_damage_percentage",
        "storage_condition_index",
        "moisture_storage_exposure",
        "quantity_kg",
    ]

    available = [
        column
        for column in numeric_candidates
        if column in dataframe.columns
    ]

    if len(available) == 0:

        return None, numeric_candidates

    # ------------------------------------------------------------------
    # We preserve the existing dataset columns and allow the saved
    # Pipeline to perform its own preprocessing.
    # ------------------------------------------------------------------

    X = dataframe[
        available
    ].copy()

    return X, []


# ======================================================================
# GET MODEL FEATURE NAMES
# ======================================================================

def get_pipeline_features(
    model
):

    # Direct estimator
    if hasattr(
        model,
        "feature_names_in_"
    ):

        return list(
            model.feature_names_in_
        )

    # Pipeline
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
# PREPARE MODEL INPUT USING SAVED MODEL SCHEMA
# ======================================================================

def prepare_model_input(
    model,
    dataframe
):

    model_features = get_pipeline_features(
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

    # Fallback to existing spoilage feature set.
    return prepare_spoilage_features(
        dataframe
    )


# ======================================================================
# NORMALIZE RISK LABELS
# ======================================================================

def normalize_risk_labels(
    values
):

    return (
        pd.Series(values)
        .astype("string")
        .str.strip()
        .str.upper()
        .fillna("UNKNOWN")
        .to_numpy(
            dtype=str
        )
    )


# ======================================================================
# CHECK PREDICTION SERVICE
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
            "spoilage_score",
            "spoilage_risk",
        ]

        missing = [
            name
            for name in required_models
            if name not in service.models
        ]

        if missing:

            print(
                "✗ Missing Spoilage models:"
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
# SPOILAGE SCORE VERIFICATION
# ======================================================================

def verify_spoilage_score(
    model,
    dataframe
):

    section(
        "SPOILAGE RISK SCORE MODEL VERIFICATION"
    )

    result = {
        "complete": False,
        "metrics": None,
    }

    print(
        "[1] Checking Spoilage Risk Score model..."
    )

    print(
        "✓ Spoilage Risk Score model loaded"
    )

    target_column = find_target_column(
        dataframe,
        [
            "spoilage_risk_score",
            "spoilage_score",
            "spoilage_risk_score_target",
        ]
    )

    if target_column is None:

        print(
            "✗ Spoilage score target not found"
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

    print(
        f"Valid target rows: {len(y_true):,}"
    )

    # --------------------------------------------------------------
    # FEATURES
    # --------------------------------------------------------------

    X, missing = prepare_model_input(
        model,
        evaluation_data
    )

    if X is None:

        print(
            "✗ Unable to prepare model features"
        )

        if missing:

            print(
                "Missing features:"
            )

            for column in missing:

                print(
                    f"  - {column}"
                )

        return result

    if missing:

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

    # --------------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------------

    print(
        "\n[2] Running Spoilage Risk Score predictions..."
    )

    try:

        predictions = model.predict(
            X
        )

    except Exception as exc:

        print(
            "✗ Spoilage Risk Score prediction failed"
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

    invalid = int(
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
        f"{invalid}"
    )

    if invalid:

        print(
            "✗ Invalid Spoilage Risk Score predictions"
        )

        return result

    if len(predictions) != len(y_true):

        print(
            "✗ Prediction/target count mismatch"
        )

        return result

    print(
        "✓ Spoilage Risk Score predictions valid"
    )

    print(
        f"Prediction range: "
        f"{predictions.min():.4f} "
        f"to "
        f"{predictions.max():.4f}"
    )

    # --------------------------------------------------------------
    # METRICS
    # --------------------------------------------------------------

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
            "✗ Spoilage score metrics failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return result

    result["metrics"] = {
        "mae": float(mae),
        "rmse": rmse,
        "r2": float(r2),
    }

    print()
    print(
        "SPOILAGE RISK SCORE METRICS"
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

    result["complete"] = True

    print(
        "\n✓ SPOILAGE RISK SCORE MODEL VERIFIED"
    )

    return result


# ======================================================================
# SPOILAGE RISK VERIFICATION
# ======================================================================

def verify_spoilage_risk(
    model,
    dataframe
):

    section(
        "SPOILAGE RISK MODEL VERIFICATION"
    )

    result = {
        "complete": False,
        "metrics": None,
    }

    print(
        "[1] Checking Spoilage Risk model..."
    )

    print(
        "✓ Spoilage Risk model loaded"
    )

    target_column = find_target_column(
        dataframe,
        [
            "spoilage_risk",
            "spoilage_risk_label",
            "spoilage_risk_category",
        ]
    )

    if target_column is None:

        print(
            "✗ Spoilage Risk target not found"
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

    # --------------------------------------------------------------
    # FEATURES
    # --------------------------------------------------------------

    X, missing = prepare_model_input(
        model,
        dataframe
    )

    if X is None:

        print(
            "✗ Unable to prepare model features"
        )

        return result

    if missing:

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

    # --------------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------------

    print(
        "\n[2] Running Spoilage Risk predictions..."
    )

    try:

        raw_predictions = model.predict(
            X
        )

    except Exception as exc:

        print(
            "✗ Spoilage Risk prediction failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return result

    y_pred = normalize_risk_labels(
        raw_predictions
    )

    invalid = int(
        np.count_nonzero(
            y_pred == "UNKNOWN"
        )
    )

    print(
        f"Prediction count: "
        f"{len(y_pred):,}"
    )

    print(
        f"Invalid predictions: "
        f"{invalid}"
    )

    if invalid:

        print(
            "✗ Invalid Spoilage Risk predictions"
        )

        return result

    print(
        "✓ Spoilage Risk predictions valid"
    )

    # --------------------------------------------------------------
    # DISTRIBUTION
    # --------------------------------------------------------------

    print()
    print(
        "SPOILAGE RISK DISTRIBUTION"
    )

    unique_values, counts = np.unique(
        y_pred,
        return_counts=True
    )

    for label, count in zip(
        unique_values,
        counts
    ):

        percentage = (
            float(count)
            /
            float(len(y_pred))
            *
            100.0
        )

        print(
            f"  {label}: "
            f"{count:,} "
            f"({percentage:.2f}%)"
        )

    # --------------------------------------------------------------
    # GROUND TRUTH
    # --------------------------------------------------------------

    y_true = normalize_risk_labels(
        dataframe[
            target_column
        ].to_numpy()
    )

    if len(y_true) != len(y_pred):

        print(
            "✗ Prediction/target count mismatch"
        )

        return result

    # --------------------------------------------------------------
    # FIXED LABEL SET
    # --------------------------------------------------------------

    standard_labels = [
        "LOW",
        "MEDIUM",
        "HIGH",
    ]

    observed = set(
        np.unique(
            np.concatenate(
                [
                    y_true,
                    y_pred,
                ]
            )
        )
    )

    labels = [
        label
        for label in standard_labels
        if label in observed
    ]

    extra_labels = sorted(
        observed
        -
        set(labels)
    )

    labels.extend(
        extra_labels
    )

    print()
    print(
        "[3] Calculating Spoilage Risk metrics..."
    )

    try:

        accuracy = accuracy_score(
            y_true,
            y_pred
        )

        precision = precision_score(
            y_true,
            y_pred,
            labels=labels,
            average="weighted",
            zero_division=0
        )

        recall = recall_score(
            y_true,
            y_pred,
            labels=labels,
            average="weighted",
            zero_division=0
        )

        f1 = f1_score(
            y_true,
            y_pred,
            labels=labels,
            average="weighted",
            zero_division=0
        )

    except Exception as exc:

        print(
            "✗ Spoilage Risk metrics failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return result

    result["metrics"] = {

        "accuracy": float(
            accuracy
        ),

        "precision": float(
            precision
        ),

        "recall": float(
            recall
        ),

        "f1": float(
            f1
        ),
    }

    print()
    print(
        "SPOILAGE RISK METRICS"
    )

    print(
        "-" * 70
    )

    print(
        f"Accuracy  : {accuracy:.6f}"
    )

    print(
        f"Precision : {precision:.6f}"
    )

    print(
        f"Recall    : {recall:.6f}"
    )

    print(
        f"F1 Score  : {f1:.6f}"
    )

    # --------------------------------------------------------------
    # CONFUSION MATRIX
    # --------------------------------------------------------------

    print()
    print(
        "Confusion Matrix:"
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels
    )

    print(
        matrix
    )

    print()
    print(
        "Labels:"
    )

    print(
        labels
    )

    result["complete"] = True

    print(
        "\n✓ SPOILAGE RISK MODEL VERIFIED"
    )

    return result


# ======================================================================
# MAIN
# ======================================================================

def main():

    section(
        "SPOILAGE PREDICTION FINAL COMPLETION CHECK"
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
        "\n[1] Checking Spoilage dataset..."
    )

    if not SPOILAGE_DATA_PATH.exists():

        print(
            "✗ Spoilage dataset not found:"
        )

        print(
            SPOILAGE_DATA_PATH
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
        "✓ Existing dataset found"
    )

    print(
        SPOILAGE_DATA_PATH
    )

    # ==================================================================
    # MODELS
    # ==================================================================

    print(
        "\n[2] Checking Spoilage models..."
    )

    if not SPOILAGE_SCORE_MODEL_PATH.exists():

        print(
            "✗ Spoilage Risk Score model not found:"
        )

        print(
            SPOILAGE_SCORE_MODEL_PATH
        )

        return

    if not SPOILAGE_RISK_MODEL_PATH.exists():

        print(
            "✗ Spoilage Risk model not found:"
        )

        print(
            SPOILAGE_RISK_MODEL_PATH
        )

        return

    print(
        "✓ Spoilage Risk Score model exists"
    )

    print(
        "✓ Spoilage Risk model exists"
    )

    # ==================================================================
    # LOAD MODELS
    # ==================================================================

    print(
        "\n[3] Loading Spoilage models..."
    )

    try:

        spoilage_score_model = joblib.load(
            SPOILAGE_SCORE_MODEL_PATH
        )

        spoilage_risk_model = joblib.load(
            SPOILAGE_RISK_MODEL_PATH
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
        "✓ Spoilage Risk Score model loaded"
    )

    print(
        f"  Type: "
        f"{type(spoilage_score_model).__name__}"
    )

    print(
        "✓ Spoilage Risk model loaded"
    )

    print(
        f"  Type: "
        f"{type(spoilage_risk_model).__name__}"
    )

    # ==================================================================
    # DATASET
    # ==================================================================

    print(
        "\n[4] Loading Spoilage dataset..."
    )

    try:

        dataframe = pd.read_csv(
            SPOILAGE_DATA_PATH
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
        "✓ Dataset loaded"
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
    # SCORE
    # ==================================================================

    score_result = verify_spoilage_score(
        spoilage_score_model,
        dataframe
    )

    # ==================================================================
    # RISK
    # ==================================================================

    risk_result = verify_spoilage_risk(
        spoilage_risk_model,
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
        "SPOILAGE PREDICTION FINAL STATUS"
    )

    score_complete = (
        score_result["complete"]
    )

    risk_complete = (
        risk_result["complete"]
    )

    print(
        "Spoilage Risk Score : "
        +
        (
            "✓ COMPLETED"
            if score_complete
            else "⚠ INCOMPLETE"
        )
    )

    print(
        "Spoilage Risk       : "
        +
        (
            "✓ COMPLETED"
            if risk_complete
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
        score_complete
        and risk_complete
        and service_valid
    )

    print()

    separator()

    if final_complete:

        print(
            "✓ SPOILAGE PREDICTION FULLY COMPLETED"
        )

        print(
            "✓ Existing Spoilage models verified"
        )

        print(
            "✓ Existing dataset verified"
        )

        print(
            "✓ Spoilage Risk Score predictions verified"
        )

        print(
            "✓ Spoilage Risk predictions verified"
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
            "LOGISTICS"
        )

    else:

        print(
            "⚠ SPOILAGE PREDICTION NOT YET COMPLETED"
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