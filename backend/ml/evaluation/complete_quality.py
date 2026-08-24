"""
QUALITY ASSESSMENT MODEL COMPLETION VERIFICATION

Existing architecture only.
Existing trained models only.
Existing processed dataset only.

No:
- model retraining
- new models
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

QUALITY_DATA_PATH = (
    DATA_DIR / "quality_features.csv"
)

QUALITY_SCORE_MODEL_PATH = (
    MODEL_DIR / "quality_score_model.joblib"
)

QUALITY_GRADE_MODEL_PATH = (
    MODEL_DIR / "quality_grade_model.joblib"
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
# QUALITY FEATURES
# ======================================================================

QUALITY_FEATURES = [

    "crop",

    "quantity_kg",

    "moisture_percentage",

    "foreign_matter_percentage",

    "damaged_percentage",

    "discolored_percentage",

    "insect_damage_percentage",

    "grain_size",

    "weight_uniformity_percentage",

    "storage_days",

    "storage_temperature_c",

    "storage_humidity_percentage",

    "total_damage_percentage",

    "storage_condition_index",

    "moisture_storage_exposure",
]


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
# PREPARE QUALITY FEATURES
# ======================================================================

def prepare_quality_features(
    dataframe
):

    missing = [

        column
        for column in QUALITY_FEATURES
        if column not in dataframe.columns
    ]

    if missing:
        return None, missing

    X = dataframe[
        QUALITY_FEATURES
    ].copy()

    return X, []


# ======================================================================
# NUMERIC TARGET
# ======================================================================

def get_numeric_target(
    dataframe,
    target_column
):

    values = pd.to_numeric(
        dataframe[target_column],
        errors="coerce"
    )

    valid_mask = (
        values.notna()
        &
        np.isfinite(
            values.to_numpy(
                dtype=float
            )
        )
    )

    return (
        dataframe.loc[valid_mask].copy(),
        values.loc[valid_mask]
        .astype(float)
        .to_numpy()
    )


# ======================================================================
# NORMALIZE GRADE LABELS
# ======================================================================

def normalize_grade_array(values):

    return (
        pd.Series(values)
        .astype("string")
        .str.strip()
        .str.upper()
        .fillna("UNKNOWN")
        .to_numpy(dtype=str)
    )


# ======================================================================
# PREDICTION SERVICE CHECK
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
            "quality_score",
            "quality_grade",
        ]

        missing = [

            name
            for name in required_models
            if name not in service.models
        ]

        if missing:

            print(
                "✗ Missing Quality models:"
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
# QUALITY SCORE
# ======================================================================

def verify_quality_score(
    model,
    dataframe
):

    section(
        "QUALITY SCORE MODEL VERIFICATION"
    )

    result = {
        "complete": False,
        "metrics": None,
    }

    print(
        "[1] Checking Quality Score model..."
    )

    print(
        "✓ Quality Score model loaded"
    )

    target_column = find_target_column(
        dataframe,
        [
            "quality_score",
            "quality_score_target",
        ]
    )

    if target_column is None:

        print(
            "✗ Quality Score target not found"
        )

        return result

    print(
        f"✓ Target: {target_column}"
    )

    target_dataframe, y_true = (
        get_numeric_target(
            dataframe,
            target_column
        )
    )

    print(
        f"Valid target rows: {len(y_true):,}"
    )

    X, missing = prepare_quality_features(
        target_dataframe
    )

    if X is None:

        print(
            "✗ Missing Quality features:"
        )

        for column in missing:

            print(
                f"  - {column}"
            )

        return result

    print(
        f"✓ Features prepared: {X.shape[1]}"
    )

    print(
        f"X shape: {X.shape}"
    )

    print(
        "\n[2] Running Quality Score predictions..."
    )

    try:

        predictions = model.predict(X)

    except Exception as exc:

        print(
            "✗ Quality Score prediction failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return result

    predictions = np.asarray(
        predictions,
        dtype=float
    )

    invalid = int(
        np.count_nonzero(
            ~np.isfinite(predictions)
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
            "✗ Invalid Quality Score predictions"
        )

        return result

    if len(predictions) != len(y_true):

        print(
            "✗ Prediction/target count mismatch"
        )

        return result

    print(
        "✓ Quality Score predictions valid"
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

    result["metrics"] = {

        "mae": float(mae),
        "rmse": rmse,
        "r2": float(r2),
    }

    print()
    print(
        "QUALITY SCORE METRICS"
    )
    print("-" * 70)

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
        "\n✓ QUALITY SCORE MODEL VERIFIED"
    )

    return result


# ======================================================================
# QUALITY GRADE
# ======================================================================

def verify_quality_grade(
    model,
    dataframe
):

    section(
        "QUALITY GRADE MODEL VERIFICATION"
    )

    result = {
        "complete": False,
        "metrics": None,
    }

    print(
        "[1] Checking Quality Grade model..."
    )

    print(
        "✓ Quality Grade model loaded"
    )

    target_column = find_target_column(
        dataframe,
        [
            "quality_grade",
            "grade",
            "quality_grade_target",
        ]
    )

    if target_column is None:

        print(
            "✗ Quality Grade target not found"
        )

        return result

    print(
        f"✓ Target: {target_column}"
    )

    X, missing = prepare_quality_features(
        dataframe
    )

    if X is None:

        print(
            "✗ Missing Quality Grade features:"
        )

        for column in missing:

            print(
                f"  - {column}"
            )

        return result

    print(
        f"✓ Features prepared: {X.shape[1]}"
    )

    print(
        f"X shape: {X.shape}"
    )

    # --------------------------------------------------------------
    # REAL PREDICTIONS
    # --------------------------------------------------------------

    print(
        "\n[2] Running Quality Grade predictions..."
    )

    try:

        raw_predictions = model.predict(X)

    except Exception as exc:

        print(
            "✗ Quality Grade prediction failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return result

    y_pred = normalize_grade_array(
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
            "✗ Invalid Quality Grade predictions"
        )

        return result

    print(
        "✓ Quality Grade predictions valid"
    )

    # --------------------------------------------------------------
    # DISTRIBUTION
    # --------------------------------------------------------------

    print()
    print(
        "QUALITY GRADE DISTRIBUTION"
    )

    unique_grades, counts = np.unique(
        y_pred,
        return_counts=True
    )

    for grade, count in zip(
        unique_grades,
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
            f"  {grade}: "
            f"{count:,} "
            f"({percentage:.2f}%)"
        )

    # --------------------------------------------------------------
    # GROUND TRUTH
    # --------------------------------------------------------------

    y_true = normalize_grade_array(
        dataframe[target_column].to_numpy()
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
        "A",
        "B",
        "C",
        "D",
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
        "[3] Calculating Quality Grade metrics..."
    )

    # --------------------------------------------------------------
    # METRICS
    # --------------------------------------------------------------

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
            "✗ Quality Grade metrics failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return result

    result["metrics"] = {

        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }

    print()
    print(
        "QUALITY GRADE METRICS"
    )
    print("-" * 70)

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

    print(matrix)

    print()
    print(
        "Labels:"
    )

    print(
        labels
    )

    result["complete"] = True

    print(
        "\n✓ QUALITY GRADE MODEL VERIFIED"
    )

    return result


# ======================================================================
# MAIN
# ======================================================================

def main():

    section(
        "QUALITY ASSESSMENT FINAL COMPLETION CHECK"
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
        "\n[1] Checking Quality dataset..."
    )

    if not QUALITY_DATA_PATH.exists():

        print(
            "✗ Quality dataset not found:"
        )

        print(
            QUALITY_DATA_PATH
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
        "✓ Quality dataset exists"
    )

    print(
        QUALITY_DATA_PATH
    )

    # ==================================================================
    # MODELS
    # ==================================================================

    print(
        "\n[2] Checking Quality models..."
    )

    if not QUALITY_SCORE_MODEL_PATH.exists():

        print(
            "✗ Quality Score model not found:"
        )

        print(
            QUALITY_SCORE_MODEL_PATH
        )

        return

    if not QUALITY_GRADE_MODEL_PATH.exists():

        print(
            "✗ Quality Grade model not found:"
        )

        print(
            QUALITY_GRADE_MODEL_PATH
        )

        return

    print(
        "✓ Quality Score model exists"
    )

    print(
        "✓ Quality Grade model exists"
    )

    # ==================================================================
    # LOAD
    # ==================================================================

    print(
        "\n[3] Loading Quality models..."
    )

    try:

        quality_score_model = joblib.load(
            QUALITY_SCORE_MODEL_PATH
        )

        quality_grade_model = joblib.load(
            QUALITY_GRADE_MODEL_PATH
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
        "✓ Quality Score model loaded"
    )

    print(
        f"  Type: "
        f"{type(quality_score_model).__name__}"
    )

    print(
        "✓ Quality Grade model loaded"
    )

    print(
        f"  Type: "
        f"{type(quality_grade_model).__name__}"
    )

    # ==================================================================
    # DATA
    # ==================================================================

    print(
        "\n[4] Loading Quality dataset..."
    )

    try:

        dataframe = pd.read_csv(
            QUALITY_DATA_PATH
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
        "✓ Quality dataset loaded"
    )

    print(
        f"  Rows    : {len(dataframe):,}"
    )

    print(
        f"  Columns : {len(dataframe.columns)}"
    )

    # ==================================================================
    # QUALITY SCORE
    # ==================================================================

    score_result = verify_quality_score(
        quality_score_model,
        dataframe
    )

    # ==================================================================
    # QUALITY GRADE
    # ==================================================================

    grade_result = verify_quality_grade(
        quality_grade_model,
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
        "QUALITY ASSESSMENT FINAL STATUS"
    )

    score_complete = (
        score_result["complete"]
    )

    grade_complete = (
        grade_result["complete"]
    )

    print(
        "Quality Score : "
        + (
            "✓ COMPLETED"
            if score_complete
            else "⚠ INCOMPLETE"
        )
    )

    print(
        "Quality Grade : "
        + (
            "✓ COMPLETED"
            if grade_complete
            else "⚠ INCOMPLETE"
        )
    )

    print(
        "PredictionService : "
        + (
            "✓ VERIFIED"
            if service_valid
            else "⚠ FAILED"
        )
    )

    final_complete = (
        score_complete
        and grade_complete
        and service_valid
    )

    print()

    separator()

    if final_complete:

        print(
            "✓ QUALITY ASSESSMENT FULLY COMPLETED"
        )

        print(
            "✓ Existing Quality models verified"
        )

        print(
            "✓ Existing Quality dataset verified"
        )

        print(
            "✓ Quality Score predictions verified"
        )

        print(
            "✓ Quality Grade predictions verified"
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
            "SPOILAGE"
        )

    else:

        print(
            "⚠ QUALITY ASSESSMENT NOT YET COMPLETED"
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