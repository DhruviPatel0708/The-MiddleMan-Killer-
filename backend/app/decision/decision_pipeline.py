"""
======================================================================
AGRICULTURE AI - DECISION PIPELINE
======================================================================

Purpose:
    End-to-end inference pipeline connecting:

        Datasets
            ↓
        Model Adapters
            ↓
        13 ML Models
            ↓
        Combined Predictions
            ↓
        Decision Intelligence Engine

IMPORTANT:
    - Uses existing trained models.
    - Does not retrain models.
    - Does not modify datasets.
    - Does not generate fake ML predictions.
======================================================================
"""

from pathlib import Path
import json

from prediction_service import PredictionService
from model_adapters import ModelAdapters
from decision_engine import DecisionIntelligenceEngine


# ======================================================================
# PATHS
# ======================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]


# ======================================================================
# DECISION PIPELINE
# ======================================================================

class DecisionPipeline:

    def __init__(self):

        print("=" * 70)
        print("AGRICULTURE AI DECISION PIPELINE")
        print("=" * 70)

        # --------------------------------------------------------------
        # Prediction service
        # --------------------------------------------------------------

        self.prediction_service = (
            PredictionService()
        )

        # --------------------------------------------------------------
        # Model adapters
        # --------------------------------------------------------------

        self.adapters = ModelAdapters(
            prediction_service=self.prediction_service
        )

        # --------------------------------------------------------------
        # Decision engine
        # --------------------------------------------------------------

        self.decision_engine = (
            DecisionIntelligenceEngine()
        )

        print("\n✓ Decision pipeline initialized.")

    # ==================================================================
    # RUN PRICE PREDICTION
    # ==================================================================

    def predict_price(self):

        result = (
            self.adapters
            .build_price_input()
        )

        prediction = (
            self.prediction_service
            .predict_one(
                "price",
                result
            )
        )

        return float(prediction)

    # ==================================================================
    # RUN DEMAND PREDICTION
    # ==================================================================

    def predict_demand(self):

        result = (
            self.adapters
            .build_demand_input()
        )

        prediction = (
            self.prediction_service
            .predict_one(
                "demand",
                result
            )
        )

        return float(prediction)

    # ==================================================================
    # RUN BUYER PREDICTION
    # ==================================================================

    def predict_buyer(self):

        return (
            self.adapters
            .predict_buyer()
        )

    # ==================================================================
    # RUN QUALITY PREDICTIONS
    # ==================================================================

    def predict_quality(self):

        return (
            self.adapters
            .predict_quality()
        )

    # ==================================================================
    # RUN LOGISTICS PREDICTIONS
    # ==================================================================

    def predict_logistics(self):

        return (
            self.adapters
            .predict_logistics()
        )

    # ==================================================================
    # RUN COST PREDICTION
    # ==================================================================

    def predict_cost(self):

        return (
            self.adapters
            .predict_cost()
        )

    # ==================================================================
    # RUN RISK PREDICTIONS
    # ==================================================================

    def predict_risk(self):

        return (
            self.adapters
            .predict_risk()
        )

    # ==================================================================
    # RUN ALL 13 MODELS
    # ==================================================================

    def generate_predictions(self):

        print("\n")
        print("=" * 70)
        print("GENERATING REAL ML PREDICTIONS")
        print("=" * 70)

        predictions = {}

        # --------------------------------------------------------------
        # 1. PRICE
        # --------------------------------------------------------------

        print("\n[1/7] Price prediction...")

        predictions["price"] = (
            self.predict_price()
        )

        print(
            f"✓ Predicted price: "
            f"{predictions['price']:.4f}"
        )

        # --------------------------------------------------------------
        # 2. DEMAND
        # --------------------------------------------------------------

        print("\n[2/7] Demand prediction...")

        predictions["demand"] = (
            self.predict_demand()
        )

        print(
            f"✓ Predicted demand: "
            f"{predictions['demand']:.4f}"
        )

        # --------------------------------------------------------------
        # 3. BUYER
        # --------------------------------------------------------------

        print("\n[3/7] Buyer reliability...")

        predictions["buyer"] = (
            self.predict_buyer()
        )

        print(
            f"✓ Buyer reliability: "
            f"{predictions['buyer']['buyer_reliability']}"
        )

        # --------------------------------------------------------------
        # 4. QUALITY + SPOILAGE
        # --------------------------------------------------------------

        print("\n[4/7] Quality and spoilage...")

        predictions["quality"] = (
            self.predict_quality()
        )

        print(
            f"✓ Quality score: "
            f"{predictions['quality']['quality_score']:.2f}"
        )

        print(
            f"✓ Quality grade: "
            f"{predictions['quality']['quality_grade']}"
        )

        print(
            f"✓ Spoilage score: "
            f"{predictions['quality']['spoilage_risk_score']:.2f}"
        )

        print(
            f"✓ Spoilage risk: "
            f"{predictions['quality']['spoilage_risk']}"
        )

        # --------------------------------------------------------------
        # 5. LOGISTICS
        # --------------------------------------------------------------

        print("\n[5/7] Logistics...")

        predictions["logistics"] = (
            self.predict_logistics()
        )

        print(
            f"✓ Transport cost: "
            f"{predictions['logistics']['transport_cost']:.2f}"
        )

        print(
            f"✓ Delay hours: "
            f"{predictions['logistics']['delay_hours']:.2f}"
        )

        print(
            f"✓ Damage percentage: "
            f"{predictions['logistics']['damage_percentage']:.2f}%"
        )

        # --------------------------------------------------------------
        # 6. COST
        # --------------------------------------------------------------

        print("\n[6/7] Cost estimation...")

        predictions["cost"] = (
            self.predict_cost()
        )

        print(
            f"✓ Estimated total cost: "
            f"{predictions['cost']['estimated_total_cost']:.2f}"
        )

        # --------------------------------------------------------------
        # 7. RISK
        # --------------------------------------------------------------

        print("\n[7/7] Transaction risk...")

        predictions["risk"] = (
            self.predict_risk()
        )

        print(
            f"✓ Payment risk: "
            f"{predictions['risk']['payment_risk']}"
        )

        print(
            f"✓ Delivery risk: "
            f"{predictions['risk']['delivery_risk']}"
        )

        print("\n" + "-" * 70)

        print(
            "✓ ALL 13 ML MODEL PREDICTIONS GENERATED"
        )

        return predictions

    # ==================================================================
    # CREATE DECISION INPUT
    # ==================================================================

    def build_decision_input(
        self,
        predictions
    ):

        """
        Convert the model predictions into a clean structure for the
        Decision Intelligence Engine.

        No fabricated values are introduced here.
        """

        decision_input = {

            "price_prediction":
                predictions["price"],

            "demand_prediction":
                predictions["demand"],

            "buyer_reliability":
                predictions["buyer"]
                ["buyer_reliability"],

            "quality_score":
                predictions["quality"]
                ["quality_score"],

            "quality_grade":
                predictions["quality"]
                ["quality_grade"],

            "spoilage_risk_score":
                predictions["quality"]
                ["spoilage_risk_score"],

            "spoilage_risk":
                predictions["quality"]
                ["spoilage_risk"],

            "transport_cost":
                predictions["logistics"]
                ["transport_cost"],

            "delay_hours":
                predictions["logistics"]
                ["delay_hours"],

            "damage_percentage":
                predictions["logistics"]
                ["damage_percentage"],

            "estimated_total_cost":
                predictions["cost"]
                ["estimated_total_cost"],

            "payment_risk":
                predictions["risk"]
                ["payment_risk"],

            "delivery_risk":
                predictions["risk"]
                ["delivery_risk"],
        }

        return decision_input

    # ==================================================================
    # RUN PIPELINE
    # ==================================================================

    def run(self):

        print("\n")
        print("=" * 70)
        print("RUNNING END-TO-END DECISION PIPELINE")
        print("=" * 70)

        # --------------------------------------------------------------
        # Generate all ML predictions
        # --------------------------------------------------------------

        predictions = (
            self.generate_predictions()
        )

        # --------------------------------------------------------------
        # Build decision input
        # --------------------------------------------------------------

        decision_input = (
            self.build_decision_input(
                predictions
            )
        )

        # --------------------------------------------------------------
        # Display combined ML output
        # --------------------------------------------------------------

        print("\n")
        print("=" * 70)
        print("COMBINED ML PREDICTIONS")
        print("=" * 70)

        print(
            json.dumps(
                decision_input,
                indent=4,
                default=str
            )
        )

        # --------------------------------------------------------------
        # Decision Engine
        # --------------------------------------------------------------

        print("\n")
        print("=" * 70)
        print("DECISION ENGINE")
        print("=" * 70)

        print(
            "\n✓ ML predictions successfully prepared."
        )

        print(
            "✓ Decision input structure created."
        )

        print(
            "\nThe existing DecisionIntelligenceEngine "
            "is ready for the final recommendation logic."
        )

        return {
            "predictions": predictions,
            "decision_input": decision_input,
        }


# ======================================================================
# TEST
# ======================================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 70)
    print("DECISION PIPELINE TEST")
    print("=" * 70)

    try:

        pipeline = DecisionPipeline()

        # --------------------------------------------------------------
        # Validate adapters first
        # --------------------------------------------------------------

        validation = (
            pipeline.adapters
            .validate_all_adapters()
        )

        if not all(
            validation.values()
        ):

            raise RuntimeError(
                "Model adapter validation failed."
            )

        # --------------------------------------------------------------
        # Run complete prediction pipeline
        # --------------------------------------------------------------

        result = pipeline.run()

        # --------------------------------------------------------------
        # Final status
        # --------------------------------------------------------------

        print("\n")
        print("=" * 70)
        print("DECISION PIPELINE TEST COMPLETED")
        print("=" * 70)

        print(
            "\n✓ 13 ML models loaded."
        )

        print(
            "✓ 7 model adapters validated."
        )

        print(
            "✓ Real predictions generated."
        )

        print(
            "✓ Combined decision input created."
        )

        print(
            "✓ No model retraining performed."
        )

        print(
            "✓ No fake prediction values generated."
        )

        print(
            "\nNext step:"
        )

        print(
            "Implement the final decision scoring and "
            "recommendation logic inside "
            "DecisionIntelligenceEngine."
        )

    except Exception as error:

        print("\n")
        print("=" * 70)
        print("DECISION PIPELINE FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        raise