"""
======================================================================
BUYER RELIABILITY MODEL COMPLETION VERIFICATION
======================================================================

Uses the existing Buyer model and existing buyers.csv.

No retraining.
No new model.
No new dataset.
No fake values.
No architecture changes.

The required engineered buyer features are recreated from the
existing buyer dataset.
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
# PROJECT PATH
# ======================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ======================================================================
# PATHS
# ======================================================================

DATA_DIR = PROJECT_ROOT / "data" / "processed"

MODEL_DIR = (
    PROJECT_ROOT
    / "backend"
    / "ml"
    / "saved_models"
)

BUYER_MODEL_PATH = (
    MODEL_DIR / "buyer_model.joblib"
)

BUYER_DATA_PATH = (
    DATA_DIR / "buyers.csv"
)


# ======================================================================
# DISPLAY
# ======================================================================

def separator():
    print("=" * 70)


def section(title):

    print("\n")
    separator()
    print(title)
    separator()


# ======================================================================
# ENGINEER BUYER FEATURES
# ======================================================================

def create_buyer_features(df):

    """
    Recreate the engineered Buyer features expected by the
    existing trained Buyer model.

    Existing source columns are used.
    """

    df = df.copy()

    # --------------------------------------------------------------
    # Safe numeric conversion
    # --------------------------------------------------------------

    numeric_columns = [

        "required_quantity_kg",
        "minimum_quantity_kg",
        "maximum_quantity_kg",
        "payment_terms_days",
        "buyer_rating",
        "total_previous_transactions",
        "successful_transactions",
        "cancelled_transactions",
        "late_payments",
        "average_payment_delay_days",
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # --------------------------------------------------------------
    # Prevent division by zero
    # --------------------------------------------------------------

    total_transactions = (
        df["total_previous_transactions"]
        .replace(0, np.nan)
    )

    # --------------------------------------------------------------
    # 1. Successful transaction rate
    # --------------------------------------------------------------

    df[
        "successful_transaction_rate"
    ] = (

        df["successful_transactions"]
        /
        total_transactions
        *
        100.0
    )

    # --------------------------------------------------------------
    # 2. Cancellation rate
    # --------------------------------------------------------------

    df[
        "cancellation_rate"
    ] = (

        df["cancelled_transactions"]
        /
        total_transactions
        *
        100.0
    )

    # --------------------------------------------------------------
    # 3. Late payment rate
    # --------------------------------------------------------------

    df[
        "late_payment_rate"
    ] = (

        df["late_payments"]
        /
        total_transactions
        *
        100.0
    )

    # --------------------------------------------------------------
    # 4. Successful transactions per total
    # --------------------------------------------------------------

    df[
        "successful_transactions_per_total"
    ] = (

        df["successful_transactions"]
        /
        total_transactions
    )

    # --------------------------------------------------------------
    # 5. Acceptable quantity range
    # --------------------------------------------------------------

    df[
        "acceptable_quantity_range_kg"
    ] = (

        df["maximum_quantity_kg"]
        -
        df["minimum_quantity_kg"]
    )

    # --------------------------------------------------------------
    # 6. Required quantity / maximum quantity
    # --------------------------------------------------------------

    maximum_quantity = (
        df["maximum_quantity_kg"]
        .replace(0, np.nan)
    )

    df[
        "required_quantity_to_max_ratio"
    ] = (

        df["required_quantity_kg"]
        /
        maximum_quantity
    )

    # --------------------------------------------------------------
    # 7. Payment delay / payment terms
    # --------------------------------------------------------------

    payment_terms = (
        df["payment_terms_days"]
        .replace(0, np.nan)
    )

    df[
        "payment_delay_to_terms_ratio"
    ] = (

        df["average_payment_delay_days"]
        /
        payment_terms
    )

    # --------------------------------------------------------------
    # Replace invalid values
    # --------------------------------------------------------------

    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # --------------------------------------------------------------
    # Fill engineered missing values
    # --------------------------------------------------------------

    engineered_columns = [

        "successful_transaction_rate",

        "cancellation_rate",

        "late_payment_rate",

        "successful_transactions_per_total",

        "acceptable_quantity_range_kg",

        "required_quantity_to_max_ratio",

        "payment_delay_to_terms_ratio",
    ]

    for column in engineered_columns:

        if column in df.columns:

            median = df[column].median()

            if pd.isna(median):
                median = 0.0

            df[column] = df[column].fillna(
                median
            )

    return df


# ======================================================================
# MODEL FEATURES
# ======================================================================

def get_model_features(
    model,
    dataframe
):

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

    return list(
        dataframe.columns
    )


# ======================================================================
# TARGET
# ======================================================================

def find_target_column(
    dataframe
):

    candidates = [

        "buyer_reliability_label",

        "buyer_reliability",

        "reliability_label",

        "reliable",

        "target",

        "label",
    ]

    for column in candidates:

        if column in dataframe.columns:

            return column

    return None


# ======================================================================
# PREDICTION SERVICE
# ======================================================================

def check_prediction_service():

    print(
        "\n[11] Checking PredictionService..."
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
                "✗ PredictionService model registry "
                "unavailable"
            )

            return False

        if "buyer" not in service.models:

            print(
                "✗ Buyer model not registered"
            )

            return False

        print(
            "✓ PredictionService contains "
            "'buyer' model"
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
        "BUYER RELIABILITY MODEL COMPLETION CHECK"
    )

    print(
        "Using existing architecture only."
    )

    print(
        "Using existing trained Buyer model only."
    )

    print(
        "Using existing buyers.csv only."
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
        "\n[1] Checking buyer dataset..."
    )

    if not BUYER_DATA_PATH.exists():

        print(
            "✗ Buyer dataset not found:"
        )

        print(
            BUYER_DATA_PATH
        )

        return

    print(
        "✓ Buyer dataset exists"
    )

    print(
        BUYER_DATA_PATH
    )

    # ==================================================================
    # MODEL
    # ==================================================================

    print(
        "\n[2] Checking saved buyer model..."
    )

    if not BUYER_MODEL_PATH.exists():

        print(
            "✗ Buyer model not found:"
        )

        print(
            BUYER_MODEL_PATH
        )

        return

    print(
        "✓ Buyer model exists"
    )

    print(
        BUYER_MODEL_PATH
    )

    # ==================================================================
    # LOAD MODEL
    # ==================================================================

    print(
        "\n[3] Loading buyer model..."
    )

    try:

        model = joblib.load(
            BUYER_MODEL_PATH
        )

        print(
            "✓ Buyer model loaded"
        )

        print(
            f"  Type: {type(model).__name__}"
        )

    except Exception as exc:

        print(
            "✗ Model loading failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return

    # ==================================================================
    # LOAD DATA
    # ==================================================================

    print(
        "\n[4] Loading buyer dataset..."
    )

    try:

        dataframe = pd.read_csv(
            BUYER_DATA_PATH
        )

        print(
            "✓ Buyer dataset loaded"
        )

        print(
            f"  Rows    : "
            f"{len(dataframe):,}"
        )

        print(
            f"  Columns : "
            f"{len(dataframe.columns)}"
        )

    except Exception as exc:

        print(
            "✗ Dataset loading failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return

    # ==================================================================
    # CREATE REQUIRED FEATURES
    # ==================================================================

    print(
        "\n[5] Creating existing engineered buyer features..."
    )

    try:

        dataframe = create_buyer_features(
            dataframe
        )

        required_engineered_features = [

            "successful_transaction_rate",

            "cancellation_rate",

            "late_payment_rate",

            "successful_transactions_per_total",

            "acceptable_quantity_range_kg",

            "required_quantity_to_max_ratio",

            "payment_delay_to_terms_ratio",
        ]

        missing_engineered = [

            column

            for column in required_engineered_features

            if column not in dataframe.columns
        ]

        if missing_engineered:

            print(
                "✗ Engineered features could not "
                "be created:"
            )

            for column in missing_engineered:

                print(
                    f"  - {column}"
                )

            return

        print(
            "✓ All required engineered features created"
        )

        for column in required_engineered_features:

            print(
                f"  ✓ {column}"
            )

    except Exception as exc:

        print(
            "✗ Buyer feature engineering failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return

    # ==================================================================
    # MODEL FEATURES
    # ==================================================================

    print(
        "\n[6] Checking model feature compatibility..."
    )

    try:

        feature_names = get_model_features(
            model,
            dataframe
        )

        missing_features = [

            feature

            for feature in feature_names

            if feature not in dataframe.columns
        ]

        if missing_features:

            print(
                "✗ Missing model features:"
            )

            for feature in missing_features:

                print(
                    f"  - {feature}"
                )

            return

        print(
            f"✓ Required model features available: "
            f"{len(feature_names)}"
        )

        X = dataframe[
            feature_names
        ].copy()

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
            "✗ Feature validation failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return

    # ==================================================================
    # PREDICTIONS
    # ==================================================================

    print(
        "\n[7] Running real buyer predictions..."
    )

    try:

        predictions = model.predict(
            X
        )

        print(
            "✓ Buyer predictions completed"
        )

    except Exception as exc:

        print(
            "✗ Buyer prediction failed"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        return

    # ==================================================================
    # VALIDATE
    # ==================================================================

    print(
        "\n[8] Validating predictions..."
    )

    predictions = np.asarray(
        predictions
    )

    print(
        f"Prediction count: "
        f"{len(predictions):,}"
    )

    if len(predictions) != len(X):

        print(
            "✗ Prediction count mismatch"
        )

        return

    if np.issubdtype(
        predictions.dtype,
        np.number
    ):

        invalid = int(
            (~np.isfinite(
                predictions.astype(float)
            )).sum()
        )

    else:

        invalid = int(
            pd.isna(
                predictions
            ).sum()
        )

    print(
        f"Invalid predictions: "
        f"{invalid}"
    )

    if invalid > 0:

        print(
            "✗ Invalid predictions found"
        )

        return

    print(
        "✓ All predictions are valid"
    )

    # ==================================================================
    # DISTRIBUTION
    # ==================================================================

    print(
        "\n[9] Buyer prediction distribution..."
    )

    prediction_series = pd.Series(
        predictions
    )

    distribution = (
        prediction_series
        .value_counts()
        .sort_index()
    )

    for label, count in distribution.items():

        percentage = (
            count
            /
            len(prediction_series)
            *
            100
        )

        print(
            f"  {label}: "
            f"{count:,} "
            f"({percentage:.2f}%)"
        )

    # ==================================================================
    # GROUND TRUTH
    # ==================================================================

    print(
        "\n[10] Checking ground-truth target..."
    )

    target_column = find_target_column(
        dataframe
    )

    metrics_available = False

    if target_column is None:

        print(
            "⚠ No buyer reliability target "
            "column found."
        )

        print(
            "Real prediction validation will "
            "be used."
        )

    else:

        print(
            f"✓ Target found: "
            f"{target_column}"
        )

        y_true = dataframe[
            target_column
        ]

        valid_mask = y_true.notna()

        y_true = (
            y_true[
                valid_mask
            ]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        y_pred = (
            pd.Series(
                predictions
            )[valid_mask]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        try:

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

            print(
                f"Accuracy  : "
                f"{accuracy:.6f}"
            )

            print(
                f"Precision : "
                f"{precision:.6f}"
            )

            print(
                f"Recall    : "
                f"{recall:.6f}"
            )

            print(
                f"F1 Score  : "
                f"{f1:.6f}"
            )

            print(
                "\nConfusion Matrix:"
            )

            print(
                confusion_matrix(
                    y_true,
                    y_pred
                )
            )

            metrics_available = True

        except Exception as exc:

            print(
                "⚠ Ground-truth metrics could "
                "not be calculated."
            )

            print(
                f"{type(exc).__name__}: {exc}"
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
        "BUYER RELIABILITY FINAL STATUS"
    )

    if target_column is not None:

        completed = (
            metrics_available
            and service_valid
        )

    else:

        completed = service_valid

    if completed:

        print(
            "✓ BUYER RELIABILITY FULLY COMPLETED"
        )

        print(
            "✓ Existing model verified"
        )

        print(
            "✓ Existing dataset verified"
        )

        print(
            "✓ Engineered features verified"
        )

        print(
            "✓ Real predictions verified"
        )

        if metrics_available:

            print(
                "✓ Evaluation metrics verified"
            )

        print(
            "✓ PredictionService integration verified"
        )

    else:

        print(
            "⚠ BUYER RELIABILITY NOT YET COMPLETED"
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