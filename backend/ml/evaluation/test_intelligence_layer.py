import os
import sys
import traceback
import joblib
import pandas as pd
import numpy as np


# ======================================================================
# PATH CONFIGURATION
# ======================================================================

CURRENT_FILE = os.path.abspath(__file__)

# D:\PythonProject3\backend\ml\evaluation\test_intelligence_layer.py
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(CURRENT_FILE), "..", "..", "..")
)

ML_DIR = os.path.join(PROJECT_ROOT, "backend", "ml")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
MODELS_DIR = os.path.join(ML_DIR, "saved_models")


# ======================================================================
# MODEL -> CORRECT DATASET MAPPING
# ======================================================================
#
# IMPORTANT:
# Each trained model MUST be tested against the feature dataset
# that was used for that model.
#
# Payment Risk and Delivery Risk both use transaction_features.csv.
# This fixes the previous feature-data mismatch.
# ======================================================================

MODEL_DATASETS = {

    # --------------------------------------------------------------
    # PRICE
    # --------------------------------------------------------------
    "price_model.joblib":
        "price_features.csv",

    # --------------------------------------------------------------
    # DEMAND
    # --------------------------------------------------------------
    "demand_model.joblib":
        "demand_features.csv",

    # --------------------------------------------------------------
    # QUALITY
    # --------------------------------------------------------------
    "quality_grade_model.joblib":
        "quality_features.csv",

    "quality_score_model.joblib":
        "quality_features.csv",

    # --------------------------------------------------------------
    # BUYER
    # --------------------------------------------------------------
    "buyer_model.joblib":
        "buyer_features.csv",

    # --------------------------------------------------------------
    # TRANSACTION / RISK
    # --------------------------------------------------------------
    #
    # These two models were trained using transaction_features.csv.
    #
    "payment_risk_model.joblib":
        "transaction_features.csv",

    "delivery_risk_model.joblib":
        "transaction_features.csv",

    # --------------------------------------------------------------
    # LOGISTICS / RISK
    # --------------------------------------------------------------
    "damage_percentage_model.joblib":
        "logistics_features.csv",

    "delay_hours_model.joblib":
        "logistics_features.csv",

    # --------------------------------------------------------------
    # SPOILAGE / QUALITY
    # --------------------------------------------------------------
    "spoilage_risk_model.joblib":
        "quality_features.csv",

    "spoilage_risk_score_model.joblib":
        "quality_features.csv",

    # --------------------------------------------------------------
    # COST
    # --------------------------------------------------------------
    "cost_estimation_model.joblib":
        "cost_features.csv",

    "transport_cost_model.joblib":
        "logistics_features.csv",
}


# ======================================================================
# MODEL GROUPS
# ======================================================================

MODEL_GROUPS = {

    "Price Prediction": [
        "price_model.joblib"
    ],

    "Demand Forecasting": [
        "demand_model.joblib"
    ],

    "Quality Assessment": [
        "quality_grade_model.joblib",
        "quality_score_model.joblib"
    ],

    "Buyer Reliability": [
        "buyer_model.joblib",
        "payment_risk_model.joblib"
    ],

    "Risk & Spillage": [
        "delivery_risk_model.joblib",
        "damage_percentage_model.joblib",
        "delay_hours_model.joblib",
        "spoilage_risk_model.joblib",
        "spoilage_risk_score_model.joblib"
    ],

    "Cost Estimation": [
        "cost_estimation_model.joblib",
        "transport_cost_model.joblib"
    ],
}


# ======================================================================
# EXPECTED FEATURE COUNTS
# ======================================================================

EXPECTED_FEATURE_COUNTS = {

    "price_model.joblib": 35,

    "demand_model.joblib": 33,

    "quality_grade_model.joblib": 15,
    "quality_score_model.joblib": 15,

    "buyer_model.joblib": 26,
    "payment_risk_model.joblib": 22,

    "delivery_risk_model.joblib": 22,
    "damage_percentage_model.joblib": 16,
    "delay_hours_model.joblib": 16,

    "spoilage_risk_model.joblib": 15,
    "spoilage_risk_score_model.joblib": 15,

    "cost_estimation_model.joblib": 19,
    "transport_cost_model.joblib": 16,
}


# ======================================================================
# UTILITY FUNCTIONS
# ======================================================================

def print_line(char="=", length=70):
    print(char * length)


def print_section(title):
    print()
    print_line()
    print(title)
    print_line()


def load_dataset(dataset_name):
    dataset_path = os.path.join(PROCESSED_DIR, dataset_name)

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(
            f"Feature dataset not found: {dataset_path}"
        )

    df = pd.read_csv(dataset_path)

    if df.empty:
        raise ValueError(
            f"Feature dataset is empty: {dataset_path}"
        )

    return df


def load_model(model_name):
    model_path = os.path.join(MODELS_DIR, model_name)

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file not found: {model_path}"
        )

    return joblib.load(model_path)


def get_model_feature_names(model):
    """
    Extract feature names from sklearn Pipeline / estimator.

    Supports:
    - Pipeline
    - models exposing feature_names_in_
    - pipeline final estimator
    """

    feature_names = None

    # --------------------------------------------------------------
    # Direct estimator
    # --------------------------------------------------------------
    if hasattr(model, "feature_names_in_"):
        try:
            feature_names = list(model.feature_names_in_)
        except Exception:
            pass

    # --------------------------------------------------------------
    # Pipeline
    # --------------------------------------------------------------
    if feature_names is None and hasattr(model, "steps"):

        # Pipeline itself
        if hasattr(model, "feature_names_in_"):
            try:
                feature_names = list(model.feature_names_in_)
            except Exception:
                pass

        # Try individual pipeline steps
        if feature_names is None:

            for _, step in reversed(model.steps):

                if hasattr(step, "feature_names_in_"):
                    try:
                        feature_names = list(
                            step.feature_names_in_
                        )
                        break
                    except Exception:
                        pass

    return feature_names


def find_missing_features(model, df):
    """
    Determine exactly which trained model features are missing
    from the selected feature dataset.
    """

    model_features = get_model_feature_names(model)

    if model_features is None:
        return [], []

    dataset_features = set(df.columns)

    missing = [
        feature
        for feature in model_features
        if feature not in dataset_features
    ]

    available = [
        feature
        for feature in model_features
        if feature in dataset_features
    ]

    return missing, available


def prepare_model_input(model, df, model_name):
    """
    Prepare a DataFrame containing EXACTLY the columns expected
    by the trained model.

    No new features are invented.
    No feature values are fabricated.
    """

    model_features = get_model_feature_names(model)

    if model_features is None:

        expected_count = EXPECTED_FEATURE_COUNTS.get(
            model_name
        )

        if expected_count is None:
            raise RuntimeError(
                f"Cannot determine expected features for "
                f"{model_name}"
            )

        # Fallback only when the model does not expose names.
        #
        # This should not normally be needed because the project
        # models are sklearn Pipelines.
        if len(df.columns) < expected_count:
            raise RuntimeError(
                f"{model_name} requires approximately "
                f"{expected_count} features, but dataset has "
                f"{len(df.columns)} columns."
            )

        return df.iloc[:, :expected_count].copy()

    missing = [
        feature
        for feature in model_features
        if feature not in df.columns
    ]

    if missing:
        raise RuntimeError(
            f"Required feature columns are missing: "
            f"{', '.join(missing)}"
        )

    X = df[model_features].copy()

    return X


def validate_input_data(X, model_name):
    """
    Validate numerical/categorical data before prediction.
    """

    if X.empty:
        raise ValueError(
            f"Input data for {model_name} is empty."
        )

    # --------------------------------------------------------------
    # Numerical validation
    # --------------------------------------------------------------
    numerical_columns = X.select_dtypes(
        include=[np.number]
    ).columns

    if len(numerical_columns) > 0:

        numerical_values = X[numerical_columns].to_numpy(
            dtype=float
        )

        if np.isnan(numerical_values).any():
            raise ValueError(
                f"NaN values detected in {model_name} input."
            )

        if np.isinf(numerical_values).any():
            raise ValueError(
                f"Infinite values detected in {model_name} input."
            )

    # --------------------------------------------------------------
    # Categorical validation
    # --------------------------------------------------------------
    categorical_columns = X.select_dtypes(
        include=["object", "category", "string"]
    ).columns

    for column in categorical_columns:

        if X[column].isna().any():
            raise ValueError(
                f"Missing categorical values in "
                f"{model_name}: {column}"
            )


def test_model(model_name):
    """
    Complete model verification.
    """

    dataset_name = MODEL_DATASETS[model_name]

    print()
    print("-" * 70)
    print(f"TESTING: {model_name}")
    print("-" * 70)

    print(f"Model:")
    print(
        os.path.join(
            MODELS_DIR,
            model_name
        )
    )

    # --------------------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------------------

    model = load_model(model_name)

    print("✓ Model loaded successfully.")
    print(
        f"✓ Model class : {type(model).__name__}"
    )

    # --------------------------------------------------------------
    # LOAD CORRECT DATASET
    # --------------------------------------------------------------

    print()
    print("Correct feature dataset:")
    print(
        os.path.join(
            PROCESSED_DIR,
            dataset_name
        )
    )

    df = load_dataset(dataset_name)

    print("✓ Dataset loaded successfully.")
    print(f"  Rows    : {len(df):,}")
    print(f"  Columns : {len(df.columns)}")

    # --------------------------------------------------------------
    # MODEL FEATURES
    # --------------------------------------------------------------

    model_features = get_model_feature_names(model)

    if model_features is not None:

        print()
        print(
            f"Model expected features : "
            f"{len(model_features)}"
        )

        print(
            f"Dataset available columns : "
            f"{len(df.columns)}"
        )

        missing = [
            feature
            for feature in model_features
            if feature not in df.columns
        ]

        if missing:

            print()
            print(
                "✗ FEATURE MISMATCH DETECTED"
            )

            print(
                "Missing features:"
            )

            for feature in missing:
                print(f"  - {feature}")

            raise RuntimeError(
                f"{model_name} feature mismatch."
            )

        print(
            "✓ All trained model features "
            "exist in the correct dataset."
        )

    # --------------------------------------------------------------
    # PREPARE INPUT
    # --------------------------------------------------------------

    X = prepare_model_input(
        model,
        df,
        model_name
    )

    print()
    print(
        f"Features selected : {len(X.columns)}"
    )

    expected_count = EXPECTED_FEATURE_COUNTS.get(
        model_name
    )

    if expected_count is not None:

        if len(X.columns) != expected_count:

            raise RuntimeError(
                f"{model_name}: expected "
                f"{expected_count} features but "
                f"prepared {len(X.columns)}."
            )

    print("✓ Model feature structure matched.")

    # --------------------------------------------------------------
    # DATA VALIDATION
    # --------------------------------------------------------------

    validate_input_data(
        X,
        model_name
    )

    print(
        "✓ Input feature values validated."
    )

    # --------------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------------

    print()
    print("Generating predictions...")

    # Use a small real subset for integration verification.
    TEST_ROWS = min(500, len(X))

    X_test = X.iloc[:TEST_ROWS].copy()

    predictions = model.predict(X_test)

    # --------------------------------------------------------------
    # PREDICTION VALIDATION
    # --------------------------------------------------------------

    if predictions is None:
        raise RuntimeError(
            f"{model_name} returned None."
        )

    predictions = np.asarray(predictions)

    if len(predictions) != TEST_ROWS:

        raise RuntimeError(
            f"{model_name}: prediction length "
            f"{len(predictions)} does not match "
            f"input length {TEST_ROWS}."
        )

    print(
        "✓ Predictions generated successfully."
    )

    print(
        "✓ Prediction length is correct."
    )

    # --------------------------------------------------------------
    # NUMERICAL PREDICTION VALIDATION
    # --------------------------------------------------------------

    if np.issubdtype(
        predictions.dtype,
        np.number
    ):

        if np.isnan(predictions).any():
            raise RuntimeError(
                f"{model_name}: NaN prediction detected."
            )

        if np.isinf(predictions).any():
            raise RuntimeError(
                f"{model_name}: Infinite prediction detected."
            )

    print(
        "✓ No NaN / Inf predictions detected."
    )

    print(
        "✓ Prediction output is valid."
    )

    # --------------------------------------------------------------
    # OUTPUT SUMMARY
    # --------------------------------------------------------------

    if np.issubdtype(
        predictions.dtype,
        np.number
    ):

        print()
        print("Prediction summary:")

        print(
            f"  min={np.min(predictions):.4f}"
        )

        print(
            f"  max={np.max(predictions):.4f}"
        )

        print(
            f"  mean={np.mean(predictions):.4f}"
        )

    else:

        unique_values = np.unique(
            predictions.astype(str)
        )

        print()
        print(
            f"Unique prediction classes : "
            f"{list(unique_values)}"
        )

    return True


# ======================================================================
# MAIN VERIFICATION
# ======================================================================

def main():

    print()
    print("=" * 70)
    print(
        "AI / INTELLIGENCE LAYER - "
        "FINAL INTEGRATION VERIFICATION"
    )
    print("=" * 70)

    print()
    print("Components:")
    print("1. Price Prediction")
    print("2. Demand Forecasting")
    print("3. Quality Assessment")
    print("4. Buyer Reliability")
    print("5. Risk & Spillage")
    print("6. Cost Estimation")

    print()
    print("No frontend.")
    print("No FastAPI.")
    print("No external API.")
    print("No new dataset.")
    print("No model training.")
    print("Existing trained models only.")

    # ==================================================================
    # 1. ENGINE INITIALIZATION
    # ==================================================================

    print_section(
        "1. AI / INTELLIGENCE ENGINE INITIALIZATION"
    )

    print(
        f"✓ Project root : {PROJECT_ROOT}"
    )

    print(
        f"✓ ML directory : {ML_DIR}"
    )

    print(
        f"✓ Data directory : {DATA_DIR}"
    )

    print(
        f"✓ Processed directory : {PROCESSED_DIR}"
    )

    if not os.path.isdir(MODELS_DIR):
        raise FileNotFoundError(
            f"Models directory not found: {MODELS_DIR}"
        )

    print(
        "✓ Models directory verified"
    )

    if not os.path.isdir(PROCESSED_DIR):
        raise FileNotFoundError(
            f"Processed directory not found: "
            f"{PROCESSED_DIR}"
        )

    print(
        "✓ Saved models directory verified"
    )

    print("✓ joblib available")
    print("✓ pandas available")
    print("✓ numpy available")

    # ==================================================================
    # 2. MODEL MODULE / ARTIFACT VERIFICATION
    # ==================================================================

    print_section(
        "2. AI MODEL MODULE VERIFICATION"
    )

    module_mapping = {
        "Price Prediction":
            "price_model.py",

        "Demand Forecasting":
            "demand_model.py",

        "Quality Assessment":
            "quality_model.py",

        "Buyer Reliability":
            "buyer_model.py",

        "Risk & Spillage":
            "risk_model.py",

        "Cost Estimation":
            "cost_model.py",
    }

    for component, filename in module_mapping.items():

        module_path = os.path.join(
            ML_DIR,
            filename
        )

        if os.path.exists(module_path):
            print(
                f"✓ {component} module verified : "
                f"{filename}"
            )
        else:
            print(
                f"⚠ {component} module not found : "
                f"{filename}"
            )

    # ==================================================================
    # 3. FEATURE DATA VERIFICATION
    # ==================================================================

    print_section(
        "3. FEATURE DATA VERIFICATION"
    )

    dataset_names = sorted(
        set(MODEL_DATASETS.values())
    )

    loaded_datasets = {}

    for dataset_name in dataset_names:

        df = load_dataset(dataset_name)

        loaded_datasets[dataset_name] = df

        print(
            f"✓ Feature file loaded : "
            f"{dataset_name} "
            f"({len(df):,} rows, "
            f"{len(df.columns)} columns)"
        )

    print(
        f"✓ Feature datasets available : "
        f"{len(loaded_datasets)}"
    )

    # ==================================================================
    # 4. TRAINED MODEL ARTIFACT VERIFICATION
    # ==================================================================

    print_section(
        "4. TRAINED MODEL ARTIFACT VERIFICATION"
    )

    loaded_models = {}

    for model_name in MODEL_DATASETS:

        model_path = os.path.join(
            MODELS_DIR,
            model_name
        )

        if not os.path.exists(model_path):

            raise FileNotFoundError(
                f"Required model missing: "
                f"{model_path}"
            )

        model = joblib.load(model_path)

        loaded_models[model_name] = model

        print(
            f"✓ {model_name} verified"
        )

        print(
            f"✓   Model class : "
            f"{type(model).__name__}"
        )

        model_features = get_model_feature_names(
            model
        )

        if model_features is not None:

            print(
                f"✓   Input features : "
                f"{len(model_features)}"
            )

    # ==================================================================
    # 5. MODEL PREDICTION INTERFACE VERIFICATION
    # ==================================================================

    print_section(
        "5. MODEL PREDICTION INTERFACE VERIFICATION"
    )

    component_results = {}

    for component, model_names in MODEL_GROUPS.items():

        component_passed = True

        for model_name in model_names:

            try:

                test_model(
                    model_name
                )

                print(
                    f"✓ {component} prediction verified : "
                    f"{model_name}"
                )

            except Exception as exc:

                component_passed = False

                print(
                    f"✗ {component} prediction failed : "
                    f"{model_name}"
                )

                print(
                    f"✗   {type(exc).__name__}: "
                    f"{exc}"
                )

        component_results[
            component
        ] = component_passed

    # ==================================================================
    # 6. COMPONENT LEVEL VERIFICATION
    # ==================================================================

    print_section(
        "6. COMPONENT LEVEL VERIFICATION"
    )

    for component, passed in component_results.items():

        if passed:

            print(
                f"✓ {component:<30}: VERIFIED"
            )

        else:

            print(
                f"✗ {component:<30}: FAILED"
            )

    # ==================================================================
    # 7. AI / INTELLIGENCE LAYER INTEGRATION
    # ==================================================================

    print_section(
        "7. AI / INTELLIGENCE LAYER INTEGRATION"
    )

    all_components_passed = all(
        component_results.values()
    )

    for component, passed in component_results.items():

        if passed:

            print(
                f"✓ {component} connected"
            )

        else:

            print(
                f"✗ {component} integration failed"
            )

    if all_components_passed:

        print(
            "✓ All AI components passed "
            "real feature-based prediction verification"
        )

    else:

        print(
            "✗ One or more AI components failed "
            "feature-based prediction verification"
        )

    # ==================================================================
    # 8. FINAL STATUS
    # ==================================================================

    print_section(
        "8. AI / INTELLIGENCE LAYER FINAL STATUS"
    )

    for component, passed in component_results.items():

        if passed:

            print(
                f"✓ {component:<30}: VERIFIED"
            )

        else:

            print(
                f"✗ {component:<30}: FAILED"
            )

    verified_count = sum(
        component_results.values()
    )

    total_count = len(
        component_results
    )

    print()
    print(
        f"Verified components : "
        f"{verified_count}/{total_count}"
    )

    print()

    if all_components_passed:

        print(
            "=" * 70
        )

        print(
            "AI / INTELLIGENCE LAYER STATUS: COMPLETE"
        )

        print(
            "=" * 70
        )

        print()
        print(
            "✓ FINAL AI / INTELLIGENCE LAYER "
            "VERIFICATION PASSED"
        )

        print()
        print(
            "✓ Existing trained models verified"
        )

        print(
            "✓ Correct feature datasets verified"
        )

        print(
            "✓ Model-to-dataset mapping verified"
        )

        print(
            "✓ Prediction interfaces verified"
        )

        print(
            "✓ All six AI components verified"
        )

        print()
        print(
            "✓ Payment Risk uses transaction_features.csv"
        )

        print(
            "✓ Delivery Risk uses transaction_features.csv"
        )

        return 0

    else:

        print(
            "=" * 70
        )

        print(
            "AI / INTELLIGENCE LAYER STATUS: FAILED"
        )

        print(
            "=" * 70
        )

        print()
        print(
            "✗ FINAL AI / INTELLIGENCE LAYER "
            "VERIFICATION FAILED"
        )

        return 1


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":

    try:

        exit_code = main()

        sys.exit(exit_code)

    except Exception as exc:

        print()
        print("=" * 70)
        print(
            "AI / INTELLIGENCE LAYER VERIFICATION FAILED"
        )
        print("=" * 70)

        print()
        print(
            f"Error Type : {type(exc).__name__}"
        )

        print(
            f"Error      : {exc}"
        )

        print()
        traceback.print_exc()

        sys.exit(1)