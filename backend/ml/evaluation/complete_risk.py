"""
======================================================================
RISK MODEL COMPLETION VERIFICATION
======================================================================

Existing architecture only.
Existing trained models only.
Existing processed dataset only.

Risk components:
    1. Payment Risk
    2. Delivery Risk

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
# EXISTING DATASET
# ======================================================================

RISK_DATA_PATH = (
    DATA_DIR / "transaction_features.csv"
)


# ======================================================================
# EXISTING MODELS
# ======================================================================

PAYMENT_RISK_MODEL_PATH = (
    MODEL_DIR / "payment_risk_model.joblib"
)

DELIVERY_RISK_MODEL_PATH = (
    MODEL_DIR / "delivery_risk_model.joblib"
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

    return dataframe.copy(), []


# ======================================================================
# LABEL NORMALIZATION
# ======================================================================

def normalize_labels(values):

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
# CLASSIFICATION MODEL VERIFICATION
# ======================================================================

def verify_risk_model(
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
    # TARGET
    # ------------------------------------------------------------------

    y_true = normalize_labels(
        dataframe[
            target_column
        ].to_numpy()
    )

    print(
        f"Valid target rows: "
        f"{len(y_true):,}"
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
        dataframe
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

        raw_predictions = model.predict(
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

    y_pred = normalize_labels(
        raw_predictions
    )

    invalid_predictions = int(
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
        f"{invalid_predictions:,}"
    )

    if invalid_predictions:

        print(
            "✗ Invalid risk predictions detected"
        )

        return result

    if len(y_pred) != len(y_true):

        print(
            "✗ Prediction/target count mismatch"
        )

        return result

    print(
        "✓ All predictions are valid"
    )

    # ------------------------------------------------------------------
    # DISTRIBUTION
    # ------------------------------------------------------------------

    print()
    print(
        f"{model_name.upper()} PREDICTION DISTRIBUTION"
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

    # ------------------------------------------------------------------
    # LABEL SET
    # ------------------------------------------------------------------

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

    # Keep common risk/payment labels in a stable order.
    preferred_labels = [
        "PAID",
        "UNPAID",
        "PENDING",
        "DELAYED",
        "ON_TIME",
        "LOW",
        "MEDIUM",
        "HIGH",
        "RELIABLE",
        "MODERATE",
        "UNRELIABLE",
        "SAFE",
        "RISKY",
    ]

    labels = [
        label
        for label in preferred_labels
        if label in observed
    ]

    remaining = sorted(
        observed
        -
        set(labels)
    )

    labels.extend(
        remaining
    )

    # ------------------------------------------------------------------
    # METRICS
    # ------------------------------------------------------------------

    print()
    print(
        "[3] Calculating evaluation metrics..."
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

    # ------------------------------------------------------------------
    # CONFUSION MATRIX
    # ------------------------------------------------------------------

    print()
    print(
        "Confusion Matrix:"
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels
    )

    print(matrix)

    print()
    print(
        "Labels:"
    )

    print(labels)

    result["metrics"] = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }

    result["complete"] = True

    print(
        f"\n✓ {model_name.upper()} MODEL VERIFIED"
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

        required_models = [
            "payment_risk",
            "delivery_risk",
        ]

        missing = [
            name
            for name in required_models
            if name not in service.models
        ]

        if missing:

            print(
                "✗ Missing Risk models:"
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
        "RISK MODEL COMPLETION CHECK"
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
        "\n[1] Checking Risk dataset..."
    )

    if not RISK_DATA_PATH.exists():

        print(
            "✗ Risk dataset not found:"
        )

        print(
            RISK_DATA_PATH
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
        "✓ Risk dataset exists"
    )

    print(
        RISK_DATA_PATH
    )

    # ==================================================================
    # MODELS
    # ==================================================================

    print(
        "\n[2] Checking Risk models..."
    )

    model_paths = {

        "Payment Risk":
            PAYMENT_RISK_MODEL_PATH,

        "Delivery Risk":
            DELIVERY_RISK_MODEL_PATH,
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
        "\n[3] Loading Risk dataset..."
    )

    try:

        dataframe = pd.read_csv(
            RISK_DATA_PATH
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
        "✓ Risk dataset loaded"
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
        "\n[4] Loading trained Risk models..."
    )

    try:

        payment_model = joblib.load(
            PAYMENT_RISK_MODEL_PATH
        )

        delivery_model = joblib.load(
            DELIVERY_RISK_MODEL_PATH
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
        "✓ Payment Risk model loaded"
    )

    print(
        f"  Type: "
        f"{type(payment_model).__name__}"
    )

    print(
        "✓ Delivery Risk model loaded"
    )

    print(
        f"  Type: "
        f"{type(delivery_model).__name__}"
    )

    # ==================================================================
    # PAYMENT RISK
    # ==================================================================

    payment_result = verify_risk_model(

        "Payment Risk",

        payment_model,

        dataframe,

        [
            "payment_risk",
            "payment_risk_label",
            "payment_status",
        ]
    )

    # ==================================================================
    # DELIVERY RISK
    # ==================================================================

    delivery_result = verify_risk_model(

        "Delivery Risk",

        delivery_model,

        dataframe,

        [
            "delivery_risk",
            "delivery_risk_label",
            "delivery_status",
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
        "RISK FINAL STATUS"
    )

    payment_complete = (
        payment_result["complete"]
    )

    delivery_complete = (
        delivery_result["complete"]
    )

    print(
        "Payment Risk       : "
        +
        (
            "✓ COMPLETED"
            if payment_complete
            else "⚠ INCOMPLETE"
        )
    )

    print(
        "Delivery Risk      : "
        +
        (
            "✓ COMPLETED"
            if delivery_complete
            else "⚠ INCOMPLETE"
        )
    )

    print(
        "PredictionService  : "
        +
        (
            "✓ VERIFIED"
            if service_valid
            else "⚠ FAILED"
        )
    )

    final_complete = (
        payment_complete
        and delivery_complete
        and service_valid
    )

    print()

    separator()

    if final_complete:

        print(
            "✓ RISK FULLY COMPLETED"
        )

        print(
            "✓ Payment Risk model verified"
        )

        print(
            "✓ Delivery Risk model verified"
        )

        print(
            "✓ Existing Risk dataset verified"
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
            "MATCHING"
        )

    else:

        print(
            "⚠ RISK NOT YET COMPLETED"
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