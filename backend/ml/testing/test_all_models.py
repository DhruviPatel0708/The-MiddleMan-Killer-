"""
FINAL ML MODEL TESTING

Tests all saved Agriculture AI models.

Checks:
    1. Model file exists
    2. Model can be loaded
    3. Required dataset can be loaded
    4. Test features can be prepared
    5. Prediction runs successfully
    6. Prediction length matches test rows
    7. Predictions contain no NaN / Inf
    8. Basic prediction output is displayed

Models:
    Buyer Reliability
    Quality Score
    Quality Grade
    Spoilage Risk Score
    Spoilage Risk
    Transport Cost
    Delay Hours
    Damage Percentage
    Cost Estimation
    Payment Risk
    Delivery Risk
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import joblib


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PATHS
# ============================================================

MODEL_DIR = (
    PROJECT_ROOT
    / "backend"
    / "ml"
    / "saved_models"
)


# ============================================================
# IMPORT DATASET PREPARATION FUNCTIONS
# ============================================================

from backend.ml.datasets.buyer_dataset import (
    prepare_buyer_dataset
)

from backend.ml.datasets.quality_dataset import (
    prepare_quality_dataset
)

from backend.ml.datasets.logistics_dataset import (
    prepare_logistics_dataset
)

from backend.ml.datasets.cost_dataset import (
    prepare_cost_dataset
)

from backend.ml.datasets.transaction_dataset import (
    prepare_transaction_dataset
)


# ============================================================
# TEST RESULT STORAGE
# ============================================================

results = []


# ============================================================
# PRINT HEADER
# ============================================================

def print_header(title):

    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# SAFE MODEL LOAD
# ============================================================

def load_saved_model(model_filename):

    model_path = MODEL_DIR / model_filename

    if not model_path.exists():

        raise FileNotFoundError(
            f"Model file not found:\n{model_path}"
        )

    model = joblib.load(
        model_path
    )

    return model, model_path


# ============================================================
# GENERIC MODEL TEST
# ============================================================

def test_model(
    model_name,
    model_filename,
    X_test
):

    print_header(
        f"TESTING: {model_name}"
    )

    try:

        # ----------------------------------------------------
        # LOAD MODEL
        # ----------------------------------------------------

        model, model_path = load_saved_model(
            model_filename
        )

        print(
            f"✓ Model loaded:"
        )

        print(
            f"  {model_path}"
        )

        # ----------------------------------------------------
        # INPUT
        # ----------------------------------------------------

        print(
            f"\nInput shape:"
        )

        print(
            f"  {X_test.shape}"
        )

        # ----------------------------------------------------
        # PREDICTION
        # ----------------------------------------------------

        print(
            "\nGenerating predictions..."
        )

        predictions = model.predict(
            X_test
        )

        predictions = np.asarray(
            predictions
        )

        # ----------------------------------------------------
        # SHAPE CHECK
        # ----------------------------------------------------

        expected_rows = len(X_test)

        if len(predictions) != expected_rows:

            raise ValueError(
                "Prediction length mismatch: "
                f"expected {expected_rows}, "
                f"got {len(predictions)}"
            )

        print(
            "✓ Prediction length:"
            f" {len(predictions):,}"
        )

        # ----------------------------------------------------
        # NAN / INF CHECK
        # ----------------------------------------------------

        if np.issubdtype(
            predictions.dtype,
            np.number
        ):

            nan_count = np.isnan(
                predictions
            ).sum()

            inf_count = np.isinf(
                predictions
            ).sum()

        else:

            nan_count = pd.isna(
                predictions
            ).sum()

            inf_count = 0

        if nan_count > 0:

            raise ValueError(
                f"NaN predictions found: "
                f"{nan_count}"
            )

        if inf_count > 0:

            raise ValueError(
                f"Infinite predictions found: "
                f"{inf_count}"
            )

        print(
            "✓ No NaN predictions"
        )

        print(
            "✓ No infinite predictions"
        )

        # ----------------------------------------------------
        # SAMPLE PREDICTIONS
        # ----------------------------------------------------

        print(
            "\nSample predictions:"
        )

        sample_count = min(
            5,
            len(predictions)
        )

        for prediction in predictions[
            :sample_count
        ]:

            print(
                f"  {prediction}"
            )

        # ----------------------------------------------------
        # CLASS DISTRIBUTION
        # ----------------------------------------------------

        if not np.issubdtype(
            predictions.dtype,
            np.number
        ):

            print(
                "\nPrediction distribution:"
            )

            print(
                pd.Series(
                    predictions
                )
                .value_counts()
                .to_string()
            )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        print(
            "\n✓ MODEL TEST PASSED"
        )

        results.append(
            {
                "Model": model_name,
                "File": model_filename,
                "Status": "PASS",
                "Test Rows": len(X_test),
                "Error": ""
            }
        )

        return True

    except Exception as error:

        print(
            "\n✗ MODEL TEST FAILED"
        )

        print(
            f"Error: {error}"
        )

        results.append(
            {
                "Model": model_name,
                "File": model_filename,
                "Status": "FAIL",
                "Test Rows": len(X_test),
                "Error": str(error)
            }
        )

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    print_header(
        "FINAL AGRICULTURE AI MODEL TESTING"
    )

    print(
        "\nModel directory:"
    )

    print(
        MODEL_DIR
    )

    print(
        "\nTesting all saved ML models..."
    )

    # ========================================================
    # LOAD DATASETS
    # ========================================================

    print_header(
        "LOADING TEST DATASETS"
    )

    # --------------------------------------------------------
    # BUYER
    # --------------------------------------------------------

    print(
        "\nLoading buyer dataset..."
    )

    buyer_data = (
        prepare_buyer_dataset()
    )

    buyer_X_test = (
        buyer_data["X_test"]
    )

    print(
        f"✓ Buyer test data: "
        f"{buyer_X_test.shape}"
    )

    # --------------------------------------------------------
    # QUALITY
    # --------------------------------------------------------

    print(
        "\nLoading quality dataset..."
    )

    quality_data = (
        prepare_quality_dataset()
    )

    quality_X_test = (
        quality_data["X_test"]
    )

    print(
        f"✓ Quality test data: "
        f"{quality_X_test.shape}"
    )

    # --------------------------------------------------------
    # LOGISTICS
    # --------------------------------------------------------

    print(
        "\nLoading logistics dataset..."
    )

    logistics_data = (
        prepare_logistics_dataset()
    )

    logistics_X_test = (
        logistics_data["X_test"]
    )

    print(
        f"✓ Logistics test data: "
        f"{logistics_X_test.shape}"
    )

    # --------------------------------------------------------
    # COST
    # --------------------------------------------------------

    print(
        "\nLoading cost dataset..."
    )

    cost_data = (
        prepare_cost_dataset()
    )

    cost_X_test = (
        cost_data["X_test"]
    )

    print(
        f"✓ Cost test data: "
        f"{cost_X_test.shape}"
    )

    # --------------------------------------------------------
    # TRANSACTION / RISK
    # --------------------------------------------------------

    print(
        "\nLoading transaction/risk dataset..."
    )

    transaction_data = (
        prepare_transaction_dataset()
    )

    transaction_X_test = (
        transaction_data["X_test"]
    )

    print(
        f"✓ Transaction test data: "
        f"{transaction_X_test.shape}"
    )

    # ========================================================
    # TEST BUYER MODEL
    # ========================================================

    test_model(
        "Buyer Reliability",
        "buyer_model.joblib",
        buyer_X_test
    )

    # ========================================================
    # TEST QUALITY MODELS
    # ========================================================

    test_model(
        "Quality Score",
        "quality_score_model.joblib",
        quality_X_test
    )

    test_model(
        "Quality Grade",
        "quality_grade_model.joblib",
        quality_X_test
    )

    test_model(
        "Spoilage Risk Score",
        "spoilage_risk_score_model.joblib",
        quality_X_test
    )

    test_model(
        "Spoilage Risk",
        "spoilage_risk_model.joblib",
        quality_X_test
    )

    # ========================================================
    # TEST LOGISTICS MODELS
    # ========================================================

    test_model(
        "Transport Cost",
        "transport_cost_model.joblib",
        logistics_X_test
    )

    test_model(
        "Delay Hours",
        "delay_hours_model.joblib",
        logistics_X_test
    )

    test_model(
        "Damage Percentage",
        "damage_percentage_model.joblib",
        logistics_X_test
    )

    # ========================================================
    # TEST COST MODEL
    # ========================================================

    test_model(
        "Cost Estimation",
        "cost_estimation_model.joblib",
        cost_X_test
    )

    # ========================================================
    # TEST RISK MODELS
    # ========================================================

    test_model(
        "Payment Risk",
        "payment_risk_model.joblib",
        transaction_X_test
    )

    test_model(
        "Delivery Risk",
        "delivery_risk_model.joblib",
        transaction_X_test
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print_header(
        "FINAL MODEL TEST SUMMARY"
    )

    results_df = pd.DataFrame(
        results
    )

    print(
        results_df[
            [
                "Model",
                "Status",
                "Test Rows"
            ]
        ]
        .to_string(
            index=False
        )
    )

    total_models = len(
        results
    )

    passed_models = (
        results_df[
            "Status"
        ]
        == "PASS"
    ).sum()

    failed_models = (
        results_df[
            "Status"
        ]
        == "FAIL"
    ).sum()

    print(
        "\n" + "-" * 70
    )

    print(
        f"Total models : {total_models}"
    )

    print(
        f"Passed       : {passed_models}"
    )

    print(
        f"Failed       : {failed_models}"
    )

    # ========================================================
    # FAILED MODELS
    # ========================================================

    if failed_models > 0:

        print(
            "\n" + "=" * 70
        )

        print(
            "FAILED MODELS"
        )

        print(
            "=" * 70
        )

        failed_df = results_df[
            results_df[
                "Status"
            ] == "FAIL"
        ]

        for _, row in failed_df.iterrows():

            print(
                f"\n{row['Model']}"
            )

            print(
                f"Error: {row['Error']}"
            )

    # ========================================================
    # FINAL STATUS
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    if failed_models == 0:

        print(
            "ALL MODEL TESTS PASSED ✓"
        )

        print(
            "=" * 70
        )

        print(
            "\n✓ All saved models loaded successfully."
        )

        print(
            "✓ All test datasets loaded successfully."
        )

        print(
            "✓ All predictions generated successfully."
        )

        print(
            "✓ Prediction lengths are correct."
        )

        print(
            "✓ No NaN/Inf predictions detected."
        )

        print(
            "\nML MODEL VALIDATION COMPLETED SUCCESSFULLY."
        )

    else:

        print(
            "MODEL TESTING COMPLETED WITH FAILURES"
        )

        print(
            "=" * 70
        )

        print(
            "\n⚠ Fix the failed models before integration."
        )

        sys.exit(1)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print(
            "\n" + "=" * 70
        )

        print(
            "FINAL MODEL TESTING FAILED"
        )

        print(
            "=" * 70
        )

        print(
            f"\nError: {error}"
        )

        sys.exit(1)