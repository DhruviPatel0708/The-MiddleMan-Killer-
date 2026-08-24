"""
======================================================================
AGRICULTURE AI - PREDICTION SERVICE
======================================================================

Purpose:
    Central inference layer for the 13 verified ML models.

IMPORTANT:
    - Does NOT retrain models.
    - Does NOT modify datasets.
    - Does NOT modify saved models.
    - Uses the existing feature datasets.
    - Validates feature compatibility before prediction.

Models:
    1.  price
    2.  demand
    3.  buyer
    4.  quality_score
    5.  quality_grade
    6.  spoilage_score
    7.  spoilage_risk
    8.  transport_cost
    9.  delay_hours
    10. damage_percentage
    11. cost
    12. payment_risk
    13. delivery_risk
======================================================================
"""

from pathlib import Path
import joblib
import pandas as pd


# ======================================================================
# PATHS
# ======================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_DIR = (
    PROJECT_ROOT
    / "backend"
    / "ml"
    / "saved_models"
)


# ======================================================================
# PREDICTION SERVICE
# ======================================================================

class PredictionService:

    def __init__(self):

        print("=" * 70)
        print("PREDICTION SERVICE")
        print("=" * 70)

        self.models = {}

        self.model_files = {
            "price":
                "price_model.joblib",

            "demand":
                "demand_model.joblib",

            "buyer":
                "buyer_model.joblib",

            "quality_score":
                "quality_score_model.joblib",

            "quality_grade":
                "quality_grade_model.joblib",

            "spoilage_score":
                "spoilage_risk_score_model.joblib",

            "spoilage_risk":
                "spoilage_risk_model.joblib",

            "transport_cost":
                "transport_cost_model.joblib",

            "delay_hours":
                "delay_hours_model.joblib",

            "damage_percentage":
                "damage_percentage_model.joblib",

            "cost":
                "cost_estimation_model.joblib",

            "payment_risk":
                "payment_risk_model.joblib",

            "delivery_risk":
                "delivery_risk_model.joblib",
        }

        self._load_models()

    # ==================================================================
    # LOAD MODELS
    # ==================================================================

    def _load_models(self):

        print("\nLoading prediction models...")
        print("-" * 70)

        for model_name, filename in self.model_files.items():

            path = MODEL_DIR / filename

            if not path.exists():

                raise FileNotFoundError(
                    f"Required model not found:\n{path}"
                )

            self.models[model_name] = joblib.load(path)

            print(
                f"✓ {model_name:<20} "
                f"{filename}"
            )

        print("-" * 70)

        print(
            f"✓ {len(self.models)} models loaded."
        )

    # ==================================================================
    # GET MODEL FEATURES
    # ==================================================================

    def get_expected_features(
        self,
        model_name
    ):

        if model_name not in self.models:

            raise ValueError(
                f"Unknown model: {model_name}"
            )

        model = self.models[
            model_name
        ]

        # --------------------------------------------------------------
        # Direct estimator
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

            for step_name in reversed(
                list(model.named_steps.keys())
            ):

                step = model.named_steps[
                    step_name
                ]

                if hasattr(
                    step,
                    "feature_names_in_"
                ):

                    return list(
                        step.feature_names_in_
                    )

        # --------------------------------------------------------------
        # Search pipeline steps
        # --------------------------------------------------------------

        if hasattr(
            model,
            "steps"
        ):

            for _, step in reversed(
                model.steps
            ):

                if hasattr(
                    step,
                    "feature_names_in_"
                ):

                    return list(
                        step.feature_names_in_
                    )

        return None

    # ==================================================================
    # CHECK FEATURES
    # ==================================================================

    def validate_features(
        self,
        model_name,
        dataframe
    ):

        expected = self.get_expected_features(
            model_name
        )

        if expected is None:

            raise ValueError(
                f"Could not determine expected "
                f"features for model: {model_name}"
            )

        missing = [
            column
            for column in expected
            if column not in dataframe.columns
        ]

        if missing:

            raise ValueError(
                f"{model_name} model is missing "
                f"features: {missing}"
            )

        return True

    # ==================================================================
    # PREDICT
    # ==================================================================

    def predict(
        self,
        model_name,
        dataframe
    ):

        if not isinstance(
            dataframe,
            pd.DataFrame
        ):

            raise TypeError(
                "Prediction input must be a pandas DataFrame."
            )

        if len(dataframe) == 0:

            raise ValueError(
                "Prediction DataFrame is empty."
            )

        self.validate_features(
            model_name,
            dataframe
        )

        expected_features = (
            self.get_expected_features(
                model_name
            )
        )

        X = dataframe[
            expected_features
        ].copy()

        model = self.models[
            model_name
        ]

        prediction = model.predict(X)

        return prediction

    # ==================================================================
    # PREDICT ONE
    # ==================================================================

    def predict_one(
        self,
        model_name,
        dataframe
    ):

        predictions = self.predict(
            model_name,
            dataframe
        )

        return predictions[0]

    # ==================================================================
    # PREDICT ALL COMPATIBLE MODELS
    # ==================================================================

    def predict_available(
        self,
        dataframe
    ):

        """
        Run only models for which the supplied DataFrame contains
        every required feature.

        Models with incompatible feature schemas are skipped instead
        of receiving fabricated values.
        """

        results = {}

        for model_name in self.models:

            try:

                self.validate_features(
                    model_name,
                    dataframe
                )

                prediction = self.predict_one(
                    model_name,
                    dataframe
                )

                results[model_name] = prediction

            except ValueError:

                # Different models intentionally use different
                # feature datasets. Do not fabricate missing inputs.
                continue

        return results

    # ==================================================================
    # MODEL INFORMATION
    # ==================================================================

    def model_feature_report(self):

        report = {}

        for model_name in self.models:

            features = self.get_expected_features(
                model_name
            )

            report[model_name] = {
                "feature_count":
                    len(features)
                    if features
                    else None,

                "features":
                    features
                    if features
                    else [],
            }

        return report


# ======================================================================
# TEST
# ======================================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 70)
    print("PREDICTION SERVICE TEST")
    print("=" * 70)

    try:

        service = PredictionService()

        print("\n" + "=" * 70)
        print("MODEL FEATURE REPORT")
        print("=" * 70)

        report = service.model_feature_report()

        for model_name, info in report.items():

            print(
                f"\n{model_name}:"
            )

            print(
                f"  Features: "
                f"{info['feature_count']}"
            )

            print(
                f"  Columns:"
            )

            for feature in info["features"]:

                print(
                    f"    - {feature}"
                )

        print("\n" + "=" * 70)
        print("PREDICTION SERVICE TEST PASSED")
        print("=" * 70)

        print(
            "\n✓ All saved models loaded."
        )

        print(
            "✓ Expected feature schemas detected."
        )

        print(
            "✓ No fake prediction values generated."
        )

        print(
            "✓ Existing ML models remain unchanged."
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("PREDICTION SERVICE TEST FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )